# Qcon-api

`qcon-api` is a question converter that enables accurate text conversion from Word into an LMS import package. It requires the frontend, `qcon-web` to work correctly. Together, these apps form the [`Qcon` service](https://qcon.ltc.bcit.ca).

## Quick Start

    docker run -p 8000:8000 registry.ltc.bcit.ca/web-apps/qcon/qcon-api

Open your browser to [http://localhost:8000](http://localhost:8000).

## Using `qcon-api`

See [Qcon Usage and Examples](https://qcon-guide.ltc.bcit.ca) for documentation about the Qcon service, including what to do after the conversion to get your questions into your LMS.

## Development

See [developing.md](docs/developing.md) for information about the technology stack.

    docker compose up --build

## Deploying `qcon-api`

`qcon-api` can be deployed as a single docker container or as a scalable Kubernetes cluster workload. We use `kpt` and `kustomize` to apply resources to a cluster based on the target environment.

## Support

If you need any help with `qcon`, please see the [Qcon Guide](https://qcon-guide.ltc.bcit.ca) or fill-out our [contact form](https://issues.ltc.bcit.ca/web-apps/qcon/qcon-user-guide).

Please submit any `qcon-api` bugs, issues, and feature requests to...[courseproduction@bcit.ca](mailto:courseproduction@bcit.ca) or [bcit-ltc/qcon](https://issues.ltc.bcit.ca/web-apps/qcon/qcon-guide).

## License

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at [https://mozilla.org/MPL/2.0/](https://mozilla.org/MPL/2.0/).
