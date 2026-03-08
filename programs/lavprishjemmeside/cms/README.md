# Lavprishjemmeside CMS

This is the remote-first CMS authority for the Lavprishjemmeside program.

## Live Surfaces

- Site: `https://lavprishjemmeside.dk`
- API: `https://api.lavprishjemmeside.dk/health`
- Repo: `ssh://theartis@cp10.nordicway.dk/home/theartis/repositories/lavprishjemmeside.dk`

## Responsibilities

- CMS and AI workflow governance
- shared SEO and ads dashboard roadmap
- control database for governed client sites
- template/bootstrap authority for new client-site installs

## Operational Note

The provisioning workflow lives in `IAn/scripts/lavpris/ssh_client_install.sh` and uses the Lavprishjemmeside control database as the authority for new client-site registrations.

This directory is not a checked-out working tree for the live CMS repo. It exists to document the authority surface inside `AI-Enterprise`.
