<!-- SPDX-License-Identifier: MPL-2.0 -->
# Qcon-api

`qcon-api` is a question converter that enables accurate text conversion from Word into a SCORM package for Learning Management Systems. It requires the frontend, `qcon-web` to work correctly. Together, these apps form the [`Qcon` service](https://qcon.ltc.bcit.ca).

## Quick Start

    docker run -p 8000:8000 ghcr.io/bcit-ltc/qcon-api

Open your browser to [http://localhost:8000](http://localhost:8000).

## Using `qcon-api`

See [Qcon Usage and Examples](https://qcon-guide.ltc.bcit.ca) for documentation about the Qcon service, including what to do after the conversion to get your questions into your LMS.

## Development

    docker compose up --build

Additional info in the CONTRIBUTING.md file.

## Support

If you need any help with `qcon`, please see the [Qcon Guide](https://qcon-guide.ltc.bcit.ca) or [contact us](mailto:ltc_techops@bcit.ca).

Please submit any `qcon-api` bugs, issues, and feature requests to the [bcit-ltc/qcon-api](https://github.com/bcit-ltc/qcon-api) source code repo.

## License

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at [https://mozilla.org/MPL/2.0/](https://mozilla.org/MPL/2.0/).
