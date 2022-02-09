//SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "../openzeppelin-contracts/contracts/token/ERC721/ERC721.sol";


contract MockERC721 is ERC721 {

    uint256 public numTokens = 0;

    mapping(uint256 => address) public royalties;

    constructor(string memory name_, string memory symbol_) ERC721(name_, symbol_){
    }

    function supportsInterface(bytes4 interfaceId) public view virtual override returns (bool) {
        return
            interfaceId == type(IERC721).interfaceId ||
            interfaceId == type(IERC721Metadata).interfaceId ||
            super.supportsInterface(interfaceId);
    }

    function mint(address to) external {
        _mint(to, numTokens);
        numTokens++;
    }


    function _mint(address to, uint256 tokenId) internal override {
        super._mint(to, tokenId);
    }
}