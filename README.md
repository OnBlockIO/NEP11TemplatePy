# NEP11TemplatePy
Fully featured NEP-11 python contract to allow to easily deploy your own NFT minting contract, and make it seamless to integrate it on GhostMarket.


## Contract overview

The contract features a generic mint() method, a burn() method, has builtin support for royalties (both GhostMarket and NEO official standard), locked content and is pausable and updatable (restricted to owner). On top of that its possible to add or remove authorized addresses, allowed to interact with the contract admin functions (pause / mint / etc.)


## What to replace

`manifest_metadata` section : fill out author/description/email accordingly

`TOKEN_SYMBOL` : replace with your desired SYMBOL

`mint` : either leave as is, to allow anyone to mint on the contract, or uncomment `verify()` to restrict minting to one of the authorized addresses


## Royalties

This template features royalties for NFT through two standard: GhostMarket standard and NEO official standard.
For each sale happening on GhostMarket trading contract, a configurable percentage will be sent to the original creator (minter) if configured (or multiple ones).
For convenience sake, both are supported on this contract, and any NFT minted support both.

The details have to be passed as an array during minting, and follow a json structure.

Note that the value is in BPS (ie 10% is 1000). We support multiple royalties, up to a maximum combined of 50% royalties. Note that if a NFT has royalties, our current implementation prevent it to be traded against indivisible currencies (like NEO), but if it does not have royalties it's allowed.

`[{"address":"NNau7VyBMQno89H8aAyirVJTdyLVeRxHGy","value":"1000"}]`
or 
`[{"address":"NNau7VyBMQno89H8aAyirVJTdyLVeRxHGy","value":1000}]`

where `NNau7VyBMQno89H8aAyirVJTdyLVeRxHGy` would be getting 10% of all sales as royalties.


## Locked Content

This template features the built-in feature of GhostMarket related to lock content. When a NFT is minted directly from GhostMarket UI with this template, you can decide to store content (which is encrypted before storing it on smart contract), which can then only be retrieved by the current NFT owner (through a custom proprietary GhostMarket API).
This is totally optional, and is currently only supported for NFT minted directly from GhostMarket (for the ones using this template), as it requires encryption before minting.

## Metadata

This contract features two methods to handle properties:

`properties` and `propertiesJson`

`properties` returns a MAP of all the NFT metadata, and is what follows NEP-11 standard (even though currently the standard is inconsistent as the signature shows it should be a MAP, while the explanation tied to it shows it should be a serialized NVM object).

`propertiesJson` returns a serialized JSON string of all the NFT metadata, and is what makes more sense for us to handle metadata.

This contract supports both methods for convenience purposes.

### Compiling contract
```
.compile.py
or
neo3-boa NEP11-Template.py
```

### Deploying from neo-cli
```
open wallet <wallet path>
deploy <nef path> <manifest.path>
```

### Upgrading from neo-cli
```
open wallet <path>
update <scripthashcontract> <nef path> <manifest path> <scripthashaddress>
```

## Testing

tests can be run with:

```
python -m unittest test_nep11
```

individual test can be run witn  
```
python -m unittest test_nep11.NEP11Test.test_nep11_decimals
```

