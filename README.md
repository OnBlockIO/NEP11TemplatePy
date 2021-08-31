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

