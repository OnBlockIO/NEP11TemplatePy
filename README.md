# NEP11TemplatePy
Fully featured NEP11 python contract to allow to easily deploy your own NFT minting contract, and make it seamless to integrate it on GhostMarket.


## Contract overview

The contract features a generic mint() method, a burn() method, has builtin support for royalties and is pausable and updatable (restricted to owner). On top of that its possible to add or remove authorized addresses, allowed to interact with the contract admin functions (pause / mint / etc.)


## What to replace

`manifest_metadata` section : fill out author/description/email accordingly

`TOKEN_SYMBOL` : replace with your desired SYMBOL

`onNEP17Payment` : either leave as is, or uncomment the section with `abort()` to prevent any NEP17 to be sent to the contract (as a failsafe, but would prevent any minting fee logic), or add your own custom logic

`mint` : either leave as is, to allow anyone to mint on the contract, or uncomment `verify()` to restrict minting to one of the authorized addresses


## Royalties

This template features royalties for NFT. For each sale happening on GhostMarket trading contract, a configurable percentage will be sent to the original creator (minter) if configured. It has to be passed as an array during minting, and follow a json structure.

Note that the value is in BPS (ie 10% is 1000). We support multiple royalties, up to a maximum combined of 50% royalties. Note that if a NFT has royalties, our current implementation prevent it to be traded against indivisible currencies (like NEO), but if it does not have royalties it's allowed.

`[{"address":"NNau7VyBMQno89H8aAyirVJTdyLVeRxHGy","value":"1000"}]`

where `NNau7VyBMQno89H8aAyirVJTdyLVeRxHGy` would be getting 10% of all sales as royalties.


## Metadata

This contract features two methods to handle properties:

`properties` and `propertiesJson`

`properties` returns a MAP of all the NFT metadata, and is what follows NEP11 standard (even though currently the standard is inconsistent as the signature shows it should be a MAP, while the explanation tied to it shows it should be a serialized NVM object).

`propertiesJson` returns a serialized JSON string of all the NFT metadata, and is what makes more sense for us to handle metadata.

This contract supports both methods for convenience purposes.

## Safe methods

Currently NEO-BOA doe not support tagging a method with a `safe` decorator. While this is optional, it is required for example if you want your NEP11 contract to use GhostMarket royalties feature, as GhostMarket trading contract checks through ABI that the `getRoyalties` is marked as `safe` to prevent potential exploits of this feature.

To do so, since BOA does not support `safe` decorator yet, simply edit the manifest file after generation, and replace the methods you want to benefit from this feature, from `safe: false` to `safe: true`

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
test_nep11.py
```

individual test can be run witn  
```
python -m unittest test_nep11.NEP11Test.test_nep11_decimals
```

