import pytest
import brownie
from brownie import Contract, MockLightNonFungibleToken, accounts
from utils.test_utils import mine_at
from utils.sha_utils import sign_message
from web3 import Web3


@pytest.fixture(scope="function")
def deployer():
    return accounts[0]


@pytest.fixture(scope="function")
def alice():
    return accounts[1]


@pytest.fixture(scope="function")
def bob():
    return accounts[2]


@pytest.fixture(scope="function")
def signer():
    return ("0x9a68219f2043f84c6f53585a25ada91cbd5f24727912942a3a05a7981185a44c",
            "0x66666666f823add319d99db0deb95cbaf762b693")


@pytest.fixture(scope="function")
def nft(deployer):
    return MockLightNonFungibleToken.deploy(
                "NonFungibleToken",  # name_
                "NFT",               # symbol_
                500,                 # collectionMaxItems_
                50,                  # maxMintsPerTx_
                10,                  # price_
                123,                 # startingTime_
                30,                  # maxWhitelistMint_
                "https://foo.bar/",  #_baseURI
                ".json",             # _extensionURI_
                {"from": deployer})


def test_constructor(nft):
    assert nft.name() == "NonFungibleToken"
    assert nft.symbol() == "NFT"
    assert nft.price() == 10
    assert nft.startingTime() == 123
    assert nft.maxMintsPerTx() == 50
    assert nft.maxWhitelistMint() == 30


def test_setMaxMintsPerTx(deployer, nft):
    assert nft.maxMintsPerTx() == 50
    nft.setMaxMintsPerTx(75, {"from": deployer})
    assert nft.maxMintsPerTx() == 75


def test_setStartingTime(deployer, nft):
    assert nft.startingTime() == 123
    nft.setStartingTime(1234, {"from": deployer})
    assert nft.startingTime() == 1234


def test_setPrice(deployer, nft):
    assert nft.price() == 10
    nft.setPrice(1337, {"from": deployer})
    assert nft.price() == 1337

    with brownie.reverts("price must be positive"):
        nft.setPrice(0, {"from": deployer})


def test_setBaseURI(deployer, nft):
    nft.mint({"from": deployer, "value": 10})
    assert nft.tokenURI(0) == "https://foo.bar/0.json"
    nft.setBaseURI("hello.world/", {"from": deployer})
    assert nft.tokenURI(0) == "hello.world/0.json"


def test_setExtensionURI(deployer, nft):
    nft.mint({"from": deployer, "value": 10})
    assert nft.tokenURI(0) == "https://foo.bar/0.json"
    nft.setExtensionURI("xyz", {"from": deployer})
    assert nft.tokenURI(0) == "https://foo.bar/0xyz"


def test_tokenURI(deployer, nft):
    nft.mint({"from": deployer, "value": 10})
    assert nft.tokenURI(0) == "https://foo.bar/0.json"
    nft.setExtensionURI("", {"from": deployer})
    assert nft.tokenURI(0) == "https://foo.bar/0"

    with brownie.reverts("ERC721URIStorage: URI query for nonexistent token"):
        nft.tokenURI(1)


def test_getOwnerNFTs(deployer, nft, alice, bob):
    nft.mint({"from": deployer, "value": 10})

    assert set(nft.getOwnerNFTs(deployer)) == {0}

    nft.mint({"from": deployer, "value": 10 * 9})
    nft.mint({"from": bob, "value": 10 * 7})
    nft.transferFrom(bob, alice, 11, {"from": bob})

    assert set(nft.getOwnerNFTs(deployer)) == set(range(10))
    assert set(nft.getOwnerNFTs(bob)) == {10, 12, 13, 14, 15, 16}
    assert set(nft.getOwnerNFTs(alice)) == {11}

    with brownie.reverts("ERC721Burnable: caller is not owner nor approved"):
        nft.burn(7, {"from": bob})

    nft.burn(13, {"from": bob})
    assert set(nft.getOwnerNFTs(bob)) == {10, 12, 14, 15, 16}

    nft.transferFrom(alice, alice, 11, {"from": alice})
    assert set(nft.getOwnerNFTs(alice)) == {11}

    assert nft.idToOwnerIndex(16) == 1
    nft.transferFrom(bob, alice, 16, {"from": bob})
    assert 16 not in list(nft.getOwnerNFTs(bob))
    assert nft.idToOwnerIndex(10) == 0
    assert nft.idToOwnerIndex(14) == 1
    assert nft.idToOwnerIndex(12) == 2
    assert nft.idToOwnerIndex(15) == 3


def test_mint(deployer, nft, alice):
    mine_at(100)
    with brownie.reverts("minting not open yet"):
        nft.mint({"from": deployer, "value": 10})

    mine_at(124)
    with brownie.reverts("not enough"):
        nft.mint({"from": alice, "value": 9})

    with brownie.reverts("limit on minting too many at a time"):
        nft.mint({"from": alice, "value": 511})

    assert nft.balance() == 0
    nft.mint({"from": alice, "value": 500})
    assert nft.balanceOf(alice) == 50
    assert nft.totalSupply() == 50
    for _ in range(9):
        nft.mint({"from": alice, "value": 500})
    assert nft.totalSupply() == 500
    assert nft.balance() == 5000


    with brownie.reverts("would exceed max supply"):
        nft.mint({"from": alice, "value": 10})


def test_whitelistMint(deployer, signer, nft, alice, bob):
    def _sign(_address, _amount, _price):
        message_hash = Web3.solidityKeccak(["address", "uint256", "uint256"],
                    [_address, _amount, _price])
        message_signed = sign_message(message_hash.hex(), signer[0])
        return message_signed.signature.hex()

    signed_alice = _sign(alice.address, 27, 10)
    with brownie.reverts("invalid arguments or not whitelisted"):
        nft.whitelistMint(28, 10, 0, signed_alice, {"from": alice})

    with brownie.reverts("invalid arguments or not whitelisted"):
        nft.whitelistMint(27, 10, 0, signed_alice, {"from": alice})

    with brownie.reverts("invalid arguments or not whitelisted"):
        nft.whitelistMint(27, 10, 0, signed_alice, {"from": bob})

    with brownie.reverts("invalid arguments or not whitelisted"):
        nft.whitelistMint(27, 10, 0, signed_alice, {"from": bob})

    nft.setSigner(signer[1], {"from": deployer})

    with brownie.reverts("invalid arguments or not whitelisted"):
        nft.whitelistMint(28, 10, 0, signed_alice, {"from": alice})

    with brownie.reverts("not enough"):
        nft.whitelistMint(27, 10, 0, signed_alice, {"from": alice})

    with brownie.reverts("invalid arguments or not whitelisted"):
        nft.whitelistMint(27, 10, 0, signed_alice, {"from": bob})

    with brownie.reverts("invalid arguments or not whitelisted"):
        nft.whitelistMint(27, 11, 0, signed_alice, {"from": alice, "value": 10})


    nft.whitelistMint(27, 10, 0, signed_alice, {"from": alice, "value": 10})
    assert nft.balanceOf(alice) == 1
    assert nft.totalSupply() == 1
    assert nft.totalWhitelistMinted() == 1

    with brownie.reverts("over account whitelist limit"):
        nft.whitelistMint(27, 10, 0, signed_alice, {"from": alice, "value": 270})

    nft.whitelistMint(27, 10, 0, signed_alice, {"from": alice, "value": 260})

    with brownie.reverts("over account whitelist limit"):
        nft.whitelistMint(27, 10, 0, signed_alice, {"from": alice, "value": 10})

    assert nft.balanceOf(alice) == 27
    assert nft.totalSupply() == 27
    assert nft.totalWhitelistMinted() == 27

    signed_bob = _sign(bob.address, 4, 10)
    with brownie.reverts("invalid arguments or not whitelisted"):
        nft.whitelistMint(4, 10, 0, signed_bob, {"from": alice, "value": 10})

    with brownie.reverts("over whitelist limit"):
        nft.whitelistMint(4, 10, 0, signed_bob, {"from": bob, "value": 40})

    nft.whitelistMint(4, 10, 0, signed_bob, {"from": bob, "value": 30})
    assert nft.balanceOf(bob) == 3
    assert nft.totalSupply() == 30
    assert nft.totalWhitelistMinted() == 30

    with brownie.reverts("over whitelist limit"):
        nft.whitelistMint(4, 10, 0, signed_bob, {"from": bob, "value": 10})

    nft.setMaxWhitelistMint(32, {"from": deployer})

    with brownie.reverts("max whitelist cannot exceed max supply"):
        nft.setMaxWhitelistMint(1000, {"from": deployer})

    with brownie.reverts("over account whitelist limit"):
        nft.whitelistMint(4, 10, 0, signed_bob, {"from": bob, "value": 20})

    nft.whitelistMint(4, 10, 0, signed_bob, {"from": bob, "value": 10})
    assert nft.balanceOf(bob) == 4
    assert nft.totalSupply() == 31
    assert nft.totalWhitelistMinted() == 31

    signed_bob2 = _sign(bob.address, 3, 0)
    nft.setMaxWhitelistMint(500, {"from": deployer})

    with brownie.reverts("over account whitelist limit"):
        nft.whitelistMint(3, 0, 4, signed_bob2, {"from": bob})

    nft.whitelistMint(3, 0, 3, signed_bob2, {"from": bob})
    assert nft.balanceOf(bob) == 7
    assert nft.totalSupply() == 34
    assert nft.totalWhitelistMinted() == 34

    with brownie.reverts("over account whitelist limit"):
        nft.whitelistMint(3, 0, 1, signed_bob2, {"from": bob})


def test_specialMint(deployer, nft, alice, bob):
    with brownie.reverts("arrays have different lengths"):
        nft.specialMint([alice, bob], [5, 10, 20])

    with brownie.reverts("arrays have different lengths"):
        nft.specialMint([alice, bob, deployer], [5, 10])

    nft.specialMint([alice, bob], [10, 20])
    assert nft.totalSupply() == 30
    assert set(nft.getOwnerNFTs(alice)) == set(range(10))
    assert set(nft.getOwnerNFTs(bob)) == set(range(10, 30))

    nft.specialMint([alice], [7])
    assert nft.totalSupply() == 37
    assert set(nft.getOwnerNFTs(alice)) == set(list(range(10)) + list(range(30, 37)))

    nft.lockSpecialMint({"from": deployer})

    with brownie.reverts("special mint permanently locked"):
        nft.specialMint([alice], [7])


def test_burn(deployer, nft, alice):
    nft.mint({"from": deployer, "value": 10})
    assert nft.balanceOf(deployer) == 1
    assert nft.totalSupply() == 1
    assert nft.getOwnerNFTs(deployer) == [0]

    with brownie.reverts("ERC721Burnable: caller is not owner nor approved"):
        nft.burn(0, {"from": alice})

    nft.burn(0, {"from": deployer})
    assert nft.balanceOf(deployer) == 0
    assert nft.totalSupply() == 1
    assert nft.getOwnerNFTs(deployer) == []

    nft.mint({"from": deployer, "value": 10})
    assert nft.balanceOf(deployer) == 1
    assert nft.totalSupply() == 2
    assert nft.getOwnerNFTs(deployer) == [1]

    nft.approve(alice, 1, {"from": deployer})
    nft.burn(1, {"from": alice})


def test_withdraw(deployer, nft, alice):
    assert nft.balance() == 0
    nft.mint({"from": deployer, "value": 10})
    assert nft.balance() == 10

    with brownie.reverts("Ownable: caller is not the owner"):
        nft.withdraw({"from": alice})

    deployer_balance_before = deployer.balance()
    nft.withdraw({"from": deployer})
    assert nft.balance() == 0
    assert (deployer.balance() - deployer_balance_before) == 10