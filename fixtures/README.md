# Synthetic fixtures

Every device record in this directory is invented. Neither file contains a captured device key.

The two valid-shape demonstration keys are:

- `FAKE!KEY?ONE#001`
- `FAKE$KEY_TWO%002`

These literals were deliberately constructed as 16 printable ASCII characters so they exercise the parser's accepted key format while remaining visibly fake. They are not credentials for any device used in this project.

`synthetic_memory.fixture` includes a duplicate record, surrounding noise, an escaped name, a key that is too short, and an unterminated JSON fragment. `expected.json` records the two valid, deduplicated keys and explicitly marks the data as synthetic.

The fixture values were compared against the private extraction archive, with **no matches**. The earlier random-looking demonstration values in the initial public commit were also checked and had no matches; they were replaced to make their purpose clearer.

The parser test suite requires exactly these fixed demonstration keys in both the expected data and the parsed fixture, so substituting captured keys causes the tests to fail.
