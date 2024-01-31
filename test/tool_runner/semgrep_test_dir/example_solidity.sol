// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TimestampCaster {
    function castTimestampToUint8() public view returns (uint8) {
        // Take the least significant 8 bits of the block timestamp
        return uint8(block.timestamp);
    }
}
