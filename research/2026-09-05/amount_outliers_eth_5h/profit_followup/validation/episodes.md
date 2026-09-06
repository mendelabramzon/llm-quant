All 20 episodes are included below. Dollar values use the frozen study's hourly endpoint marks and are rounded for display; exact wei accounting is in [ledger.json](ledger.json). These are retained on-chain episode proceeds, before operating costs, failed attempts, later payments or rebates.

| Block | Brief LP venue | Gross USD | Direct payment USD | Gas USD | Retained USD | Output improvement without opening, bps |
|---|---|---:|---:|---:|---:|---:|
| [25910849](https://etherscan.io/block/25910849) | Uniswap v4 | 26.83 | 25.36 | 0.19 | 1.28 | 50.13 |
| [25910935](https://etherscan.io/block/25910935) | Uniswap v3 | 16.26 | 15.56 | 0.17 | 0.53 | 16.86 |
| [25910990](https://etherscan.io/block/25910990) | Ekubo v3 | 74.32 | 70.56 | 0.20 | 3.56 | 184.31 |
| [25910995](https://etherscan.io/block/25910995) | Uniswap v4 | 0.68 | 0.40 | 0.14 | 0.14 | 193.60 |
| [25911033](https://etherscan.io/block/25911033) | Uniswap v4 | 2.87 | 2.64 | 0.15 | 0.08 | 101.29 |
| [25911089](https://etherscan.io/block/25911089) | Ekubo v3 | 3.14 | 2.86 | 0.15 | 0.12 | 203.81 |
| [25911110](https://etherscan.io/block/25911110) | No matched position | 5.65 | 5.31 | 0.16 | 0.19 | 309.15 |
| [25911337](https://etherscan.io/block/25911337) | Uniswap v4 | 36.74 | 27.29 | 0.54 | 8.91 | 581.89 |
| [25911349](https://etherscan.io/block/25911349) | Uniswap v4 | 98.58 | 93.98 | 0.28 | 4.33 | 60.07 |
| [25911429](https://etherscan.io/block/25911429) | Ekubo v3 | 3.68 | 3.34 | 0.23 | 0.11 | 50.19 |
| [25911582](https://etherscan.io/block/25911582) | Ekubo v3 | 4.83 | 3.61 | 0.28 | 0.95 | 101.19 |
| [25911701](https://etherscan.io/block/25911701) | Uniswap v4 | 10.03 | 9.39 | 0.23 | 0.41 | 49.78 |
| [25911742](https://etherscan.io/block/25911742) | No matched position | 1.03 | 0.52 | 0.27 | 0.23 | 83.23 |
| [25911771](https://etherscan.io/block/25911771) | Ekubo v2 | 10.96 | 10.24 | 0.33 | 0.39 | 309.22 |
| [25911802](https://etherscan.io/block/25911802) | Uniswap v4 | 9.80 | 7.42 | 0.26 | 2.12 | 526.24 |
| [25911874](https://etherscan.io/block/25911874) | Ekubo v3 | 0.92 | 0.27 | 0.56 | 0.09 | 100.52 |
| [25911943](https://etherscan.io/block/25911943) | Ekubo v3 | 22.56 | 21.58 | 0.27 | 0.71 | 203.99 |
| [25911995](https://etherscan.io/block/25911995) | No matched position | 32.33 | 30.79 | 0.19 | 1.35 | 1.01 |
| [25912028](https://etherscan.io/block/25912028) | Uniswap v3 | 4.82 | 3.29 | 0.48 | 1.06 | 99.17 |
| [25912097](https://etherscan.io/block/25912097) | Ekubo v2 | 14.61 | 13.65 | 0.28 | 0.67 | 137.40 |
| **Total** | **17 matched positions** | 380.62 | 348.04 | 5.35 | 27.23 | — |

Output improvement is `(without-opening output − actual output) / actual output × 10,000`, at the explicitly identified recipient in [audit.json](audit.json). These include some settlement/route contracts. Different output assets are not summed together. Gas effects on the middle transaction are saved separately.

| Block | Opening transaction | Middle order | Closing transaction |
|---|---|---|---|
| 25910849 | [0x74342e719f…](https://etherscan.io/tx/0x74342e719fe591b84a0a3cadab143e1cda1a5426566d66ed1bb1b9f905ca9927) | [0xe89173edc4…](https://etherscan.io/tx/0xe89173edc4548cbb3120b183d7b2cf8a5aa56f225410545d5bb9403901e3a27d) | [0xe490aa892b…](https://etherscan.io/tx/0xe490aa892b439edf2d14260624d750be012c3b5fb033f796e4ffa11773c37d2c) |
| 25910935 | [0xac07db9dfc…](https://etherscan.io/tx/0xac07db9dfcb250401b6d08dc1c535359ba935e5fc218cfdf3e4809ad830417b3) | [0xf814e3bf9b…](https://etherscan.io/tx/0xf814e3bf9b9febeda214244746db4e620240847a17cc8ac4e125248013d41b9f) | [0xe9261740c1…](https://etherscan.io/tx/0xe9261740c1496b1ea281abcd42643e9e1ddfab8447f392ddc9ac995890345aa2) |
| 25910990 | [0xeaa3904392…](https://etherscan.io/tx/0xeaa390439220f8c77c49e33d24f5ccf65dd4a734c1ca6512314d3d7403eb6d69) | [0x00b7ccd9b7…](https://etherscan.io/tx/0x00b7ccd9b7b6d77bec2b1cb695f2af5d131ea8ae9e49d0a394005acf40f554e0) | [0x7f41405137…](https://etherscan.io/tx/0x7f414051379892bca5272033bda8544cbf73ccad0f28573fed1528d8cae7758c) |
| 25910995 | [0xed4d95b24d…](https://etherscan.io/tx/0xed4d95b24d00d9ce49fe3e381b5bae366535717670d0131f77cdab3e92fd72ec) | [0xc4a0a6f271…](https://etherscan.io/tx/0xc4a0a6f27119c7298dff9d2272825ea274745b70965830cd9cc5dfd8f1c23b16) | [0xb6eabef86d…](https://etherscan.io/tx/0xb6eabef86d2ac23564ec1883fad0ed597d14474256aad623843eb31514a903fe) |
| 25911033 | [0x5653d96262…](https://etherscan.io/tx/0x5653d962621406f202bfabbc6d07f7b7f63c8f3f72062af1247c37a0bfd3d4ae) | [0x5c72963f34…](https://etherscan.io/tx/0x5c72963f346b79d81d9d6cb3ebec6ff1b6863694b041de0400cd45d859e1cf36) | [0xe7853bfa02…](https://etherscan.io/tx/0xe7853bfa0228443c96558bf4f8ac2920750d383f3a86748a87f6594eb2adcd99) |
| 25911089 | [0xcae0ea032c…](https://etherscan.io/tx/0xcae0ea032c49cd58bf4dbaad0961098aceb02d45d0141fd83eab600a86327181) | [0xd7f63bc362…](https://etherscan.io/tx/0xd7f63bc362c297afb5c83c85d29b189d0f24ec301c641500a1c6c15cfc08e82a) | [0x2ea4ca5588…](https://etherscan.io/tx/0x2ea4ca5588fcd4950f6c8a6f90ebeb71fa8a2d4009efecd9079526aa5afeb2fc) |
| 25911110 | [0x15ddfa453d…](https://etherscan.io/tx/0x15ddfa453d061993f0111e477366d8b3f756a10c108787ba88ddfdb2fbf78a8e) | [0xcfb4db3041…](https://etherscan.io/tx/0xcfb4db30418a077f63f039fa05a4c00a73ac05dbec7fca5e912d4c2a38aac355) | [0x9461b7cf91…](https://etherscan.io/tx/0x9461b7cf91f6c6874fbb0b09f87f071b92398154f4c428bcae387ae145b339d1) |
| 25911337 | [0x0cd296fb5f…](https://etherscan.io/tx/0x0cd296fb5fc64475ec5f2eadffd1ca1a4e6ceca1943d1e6e335b3fc01d0cfed4) | [0xe4f5790bbb…](https://etherscan.io/tx/0xe4f5790bbbe29255023f6bff438db7a2af8bbef500a8df94d7aefc6fd8fe2d3f) | [0x71f1ed1361…](https://etherscan.io/tx/0x71f1ed1361ab7d018d31c2862184b83b6ebc4206951574e5ea3d7ce3ea5c3a28) |
| 25911349 | [0x8f5c4a2987…](https://etherscan.io/tx/0x8f5c4a2987be2029e4a6430eeed76e657277118c4afbbd93fa72f741aea0079c) | [0xe0697c2f09…](https://etherscan.io/tx/0xe0697c2f09539eb759c9ca423bb6f48001916217310222fbe724478d5dddb78d) | [0xbfd942c15d…](https://etherscan.io/tx/0xbfd942c15d60f697d4af3673c0cc9cd882b122332d05071c5fc8d5d0301f7790) |
| 25911429 | [0x59653603f1…](https://etherscan.io/tx/0x59653603f1b9818ba0003b8ac68f3155e7006204512348576f01b99fb891fb28) | [0xefd80d4f31…](https://etherscan.io/tx/0xefd80d4f3104927a0a77f89f4fd8ae60d45957ec1e32eb42d1f76ba1b30f515a) | [0x1878a99580…](https://etherscan.io/tx/0x1878a99580c43778346ea300e95ec67973eb200f6ba1767fe2c086cc71dc7363) |
| 25911582 | [0x8974901eae…](https://etherscan.io/tx/0x8974901eaeca380afd31024edb86f147e1be5acf42ef5ac7b5c8fdd06920d390) | [0x8d8439c643…](https://etherscan.io/tx/0x8d8439c643669fd4f74daad30a09997747fb18f30821a8c06a93382a2b685425) | [0x6b2409efc3…](https://etherscan.io/tx/0x6b2409efc370499000ad679809f36705f288209c49f41e0ea9f5a188e64cb2e4) |
| 25911701 | [0x1c135c5fa4…](https://etherscan.io/tx/0x1c135c5fa4eda3580dfee5bb32c1ae9a418ec612afb3fa550d74b0b016190ba9) | [0xbedf49d7d0…](https://etherscan.io/tx/0xbedf49d7d05f42bc593d9ad9446d1239f361486f7d58addcc73fa2771f2fc69f) | [0x07911b27c0…](https://etherscan.io/tx/0x07911b27c06a75a686ac6c2c80546b3a362c37c9a997099cfd769ff8cc01fbc9) |
| 25911742 | [0x6942ba0394…](https://etherscan.io/tx/0x6942ba0394a24f417c7e78192bc361e04cd00a2655fb26741203fca0a99891aa) | [0x8b1f7d5719…](https://etherscan.io/tx/0x8b1f7d57194c60c1e5cf7523714a519ff1e00a01e25f84dd0c3e79aa7af75832) | [0xeb1ad9cf3e…](https://etherscan.io/tx/0xeb1ad9cf3e402277b893f3b1ec5cc4540835e58dd80ed84fc5e7ec88afa7fcf4) |
| 25911771 | [0xcae533f0e6…](https://etherscan.io/tx/0xcae533f0e6db0696acccd392d4c52ee3d6de58ac95cb6086b69b1c83caa47413) | [0x94eb4ae4cf…](https://etherscan.io/tx/0x94eb4ae4cf65c69f032eb5bdc2f515acfdc7799568d443b45546a570e5f77046) | [0x3c879fa600…](https://etherscan.io/tx/0x3c879fa600a3fe8a5a69514e557c7ae0c0caa7d96ff4eb752ae2237b2744268a) |
| 25911802 | [0x1aa3afeb6a…](https://etherscan.io/tx/0x1aa3afeb6a85c6c3cd4b595cfeeb77a7321a2b35dd8d6c579863bda5f642d948) | [0x9de0b5e26a…](https://etherscan.io/tx/0x9de0b5e26a50e5cbfb3dfe2bbe0c11ac7907052223a014e6e5dfbd508a933bff) | [0x591ba402d0…](https://etherscan.io/tx/0x591ba402d0d11e079010bd91072c48d7a80f15c74bfcd31831652aecb18ed424) |
| 25911874 | [0xfbb2cdfa6f…](https://etherscan.io/tx/0xfbb2cdfa6f1dfeac53d2dea46e082d3ff0b721945b56f08766110172124db6f0) | [0x7bd7e48f28…](https://etherscan.io/tx/0x7bd7e48f286c050e8287f3ed47d424d94b10c52ba7d0906bfcbec1c8c5d08859) | [0x6301da10c1…](https://etherscan.io/tx/0x6301da10c1a3746fe0394ec7ccbf47498834211e70920cdb1d4407ead832581a) |
| 25911943 | [0x05dadda2e5…](https://etherscan.io/tx/0x05dadda2e58b1ab789cc3974857c97de77e00ff8e92c5a19f1866c870104fd0b) | [0xd6472cd805…](https://etherscan.io/tx/0xd6472cd8053016ce84b86b7c84eb63ea1432e0fedf5f9d5443587b15d543f2d8) | [0x93730a5674…](https://etherscan.io/tx/0x93730a56745d5b07553814c45372daf2ace0d2f21b864ee7fef03ff6f434e942) |
| 25911995 | [0x67a23ceeb0…](https://etherscan.io/tx/0x67a23ceeb08a41ac3fa9cc0fe3557610a4531b791999ff477a6a5470c5cfcd1e) | [0xb19179a96e…](https://etherscan.io/tx/0xb19179a96eb27cb0fb05f08443c9634198423adf0f8f6d0944a5ba6b9a07641f) | [0x90c68d2146…](https://etherscan.io/tx/0x90c68d21460c9752b8bbe536a8e052627b0069c71299cc908d177288d28891df) |
| 25912028 | [0x10c555876d…](https://etherscan.io/tx/0x10c555876d40d2dbd731e5a31eb55c58f6cf94479385f843bf04d91eb2cd86bc) | [0x06dd2ba089…](https://etherscan.io/tx/0x06dd2ba089855125f975804d0330da92ac48f364a2e0901d4733ed8cc447c384) | [0x0de739c1ce…](https://etherscan.io/tx/0x0de739c1ced8e47e3b3c78439a81b19978bac596d9f999c29a6af101716fbf47) |
| 25912097 | [0x521f849946…](https://etherscan.io/tx/0x521f8499462136e04beba6f3c58095e7c8316929c1c784c0a5f5aaa2b6dee8d0) | [0x1e7729f9e8…](https://etherscan.io/tx/0x1e7729f9e8278a4204e629d62f093852eb15f5c99e910344d65eaf51cd644462) | [0xc2ab91a8ae…](https://etherscan.io/tx/0xc2ab91a8ae7574fce3cc8dbb252593f4e6d776877c9dc38b57338f9e0b4be98b) |
