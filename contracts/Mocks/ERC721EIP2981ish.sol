//SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "../openzeppelin-contracts/contracts/token/ERC721/ERC721.sol";


contract ERC721EIP2981ish is ERC721 {

    uint256 public royaltiesNum;
    uint256 public constant ROYALTIES_DENOM = 1000;
    uint256 public numTokens = 0;

    mapping(uint256 => address) public royalties;

    constructor(string memory name_, string memory symbol_, uint256 royaltiesNum_) ERC721(name_, symbol_){
        royaltiesNum = royaltiesNum_;
    }

    function supportsInterface(bytes4 interfaceId) public view virtual override returns (bool) {
        return
            interfaceId == type(IERC721).interfaceId ||
            interfaceId == type(IERC721Metadata).interfaceId ||
            super.supportsInterface(interfaceId) ||
            interfaceId == 0x2a55205a;
    }

    function mint(address to) external {
        _mint(to, numTokens);
        numTokens++;
    }


    function _mint(address to, uint256 tokenId) internal override {
        super._mint(to, tokenId);
        royalties[tokenId] = msg.sender;
    }

    // royaltyAmount returns the net price after royalties.
    function royaltyInfo(uint256 _tokenId, uint256 _salePrice) external view
        returns (address receiver, uint256 royaltyAmount){
            uint256 _royalties = (_salePrice * royaltiesNum) /  ROYALTIES_DENOM;
            return (royalties[_tokenId], _salePrice - _royalties);
    }
}