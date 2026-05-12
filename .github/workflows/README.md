<!--
SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>

SPDX-License-Identifier: Apache-2.0
-->

## Updating Github Actions

All Github Actions are pinned to a specific commit hash to ensure integrity (if an attacker were to compromise the Github Actions infrastructure, they would not be able to execute arbitrary code in our workflows).

To make it easier to update the pinned commit hash, use https://github.com/mheap/pin-github-action (easiest way is the Docker flow)
