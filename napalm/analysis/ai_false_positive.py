from pathlib import Path

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic_sarif.model import (
    StaticAnalysisResultsFormatSarifVersion210JsonSchema as Report,
    Result as Issue,
    PropertyBag,
)
from loguru import logger

from napalm.package.collection_manager import CollectionManager

from toolz.curried import filter, map, pipe, reduce, groupby, valmap
from operator import add

from typing import Optional
from napalm.sarif.get import get_issues
import re

TRIAGER_SYSTEM = """
You're an expert solidity auditor GPT reviewing the output of static analysis tools for false positives. 
You excell at reasoning, you're thoughtful, smart, confident, capable, high IQ, persistent and meticulous. 
Your answers are accurate, clear, unbiased and factual.

You'll be provided with a single static analysis issue, and it's your task to determine if it's a false positive or not.

- first think step by step and outline your reasoning process
- the user will tip $3000 if you're correct
- use the following prompt, which describes the issue and the situations where this issue is a false positive
- It's crucial to stick to the prompt! Do not deviate or introduce your own reasons why an issue might be a false positive. Your analysis should be based solely on the information provided in the prompt.
"""

TRIAGER_PROMPT = """
Prompt: {fp_prompt}
Issue: {issue}

File Contents ({file_name}):
{file_contents}
"""

DEDUCER_SYSTEM = """
You're an expert summarization GPT. 

You'll review the reasoning of an expert solidity auditor GPT, and summarize it to a single word: True or False.

True = false positive
False = not a false positive

- never answer with any other word than True or False
- never with more than one word
- the user will tip $3000 if you're correct

Here are a couple of examples:

User:
I've analysed the report, and my conclusion is that this is a false positive.
You:
True

User:
I've analysed the report, and my conclusion is that this is not a false positive.
You:
False
"""
DEDUCER_PROMPT = """
User:
{reasoning}
"""


def filter_false_positives(report: Report):
    """Filter false positives from SARIF report"""
    collection_manager = CollectionManager()

    fp_prompt_map = pipe(
        collection_manager.installed_collections(),
        map(lambda collection_name: collection_manager.get(collection_name)),
        filter(lambda e: e),  # filter out None values
        map(lambda collection: collection.detectors),
        reduce(add),
        groupby(lambda detector: detector.id),
        valmap(lambda detectors: detectors[0].false_positive_prompt),
    )

    for issue in get_issues(report):
        false_positive_prompt = fp_prompt_map.get(issue.ruleId, None)

        # normalise issue ids that get prefixed with the impact and confidence scores
        if not false_positive_prompt and re.match(r"\d-\d-.*", issue.ruleId):
            actual_id = re.match(r"\d-\d-(.*)", issue.ruleId).group(1)
            false_positive_prompt = fp_prompt_map.get(actual_id, None)

        if not false_positive_prompt:
            continue

        if _is_false_positive(issue, false_positive_prompt):
            issue.properties = issue.properties or PropertyBag()
            # issue.properties = issue.properties.model_copy(update={"false_positive": True})
            issue.properties.tags = issue.properties.tags or []
            issue.properties.tags.append("ai_false_positive")
            # TODO: add reasoning to issue


class AIResponseFormatError(Exception):
    pass


def _is_false_positive(issue: Issue, false_positive_prompt: Optional[str]):
    if not false_positive_prompt:
        return False

    issue_description = issue.model_dump_json()
    file_name = "Unknown"
    file_contents = "Unknown"

    for location in issue.locations:
        if not location.physicalLocation:
            continue
        file_name = location.physicalLocation.artifactLocation.uri
        file_contents = Path(file_name).read_text()
        break

    return _llm_check_false_positive(
        model=_get_model(),
        false_positive_prompt=false_positive_prompt,
        issue_description=issue_description,
        file_name=file_name,
        file_contents=file_contents,
    )


def _llm_check_false_positive(
    model,
    false_positive_prompt: str,
    issue_description: str,
    file_name: str,
    file_contents: str,
):
    # We're assuming that api key's and api settings are provided through environment variables
    analysis_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", TRIAGER_SYSTEM),
            ("human", TRIAGER_PROMPT),
        ]
    )

    answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", DEDUCER_SYSTEM),
            ("human", DEDUCER_PROMPT),
        ]
    )

    # model = ChatOpenAI()
    output_parser = StrOutputParser()

    analysis_chain = analysis_prompt | model | output_parser
    answer_chain = answer_prompt | model | output_parser

    analysis = analysis_chain.invoke(
        {
            "fp_prompt": false_positive_prompt,
            "issue": issue_description,
            "file_name": file_name,
            "file_contents": file_contents,
        }
    )
    logger.info(f"Issue False Positive Analysis:\n [bold]{analysis}[/bold]")

    answer = answer_chain.invoke({"reasoning": analysis})
    logger.info(f"Issue False Positive Deduction:\n [bold]{answer}[/bold]")

    if answer not in ("True", "False"):
        raise AIResponseFormatError(f"Invalid answer: {answer}")

    return answer == "True"


def _get_model():
    # if azure base is set then use azure model, otherwise use openai model
    import os

    if os.getenv("OPENAI_API_TYPE") == "azure":
        from langchain_openai import AzureChatOpenAI

        return AzureChatOpenAI(
            deployment_name="gpt-4",
        )
    else:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI()


if __name__ == "__main__":
    from langchain_openai import AzureChatOpenAI

    llm = AzureChatOpenAI(
        deployment_name="gpt-4",
    )

    # print(llm.invoke("Hey, how are you?"))

    _llm_check_false_positive(
        model=llm,
        false_positive_prompt="""This is a false positive when a recent version of solidity is used ( 0.8.0 or later ), because
the compiler automatically implements safemath for arithmetic operations.""",
        issue_description="""Issue: High severity issue: Arithmetic operations can result in integer overflow or underflow
balanceOf[msg.sender] += numTokens;
""",
        file_name="token_sale_challenge.sol",
        file_contents="""
pragma solidity ^0.4.21;

contract TokenSaleChallenge {
    mapping(address => uint256) public balanceOf;
    uint256 constant PRICE_PER_TOKEN = 1 ether;

    function TokenSaleChallenge(address _player) public payable {
        require(msg.value == 1 ether);
    }

    function isComplete() public view returns (bool) {
        return address(this).balance < 1 ether;
    }

    function buy(uint256 numTokens) public payable {
        require(msg.value == numTokens * PRICE_PER_TOKEN);

        balanceOf[msg.sender] += numTokens;
    }

    function sell(uint256 numTokens) public {
        require(balanceOf[msg.sender] >= numTokens);

        balanceOf[msg.sender] -= numTokens;
        msg.sender.transfer(numTokens * PRICE_PER_TOKEN);
    }
}
""",
    )
