# Caravan

[![CodeFactor](https://www.codefactor.io/repository/github/bdmbdsm/openprocurement.caravan/badge/dev)](https://www.codefactor.io/repository/github/bdmbdsm/openprocurement.caravan/overview/dev)

The purpose of caravan is to interconnect web resources in "if this than that" manner. Also the project was built with extensibility and simplicity in mind, so you're welcome to contribute.

## Documentation

There are some diagrams, describing workflow and code structure of the project. You can find them in `docs/caravan.xml` and open them with [draw.io](https://draw.io)

## Summary

- Testing
- TODO -> How it works

## Testing

Almost all of the present tests are environment-dependent.
It means, that they require working webapps and db to success.

So, environment-independent tests could be run separately.

Run all tests:
`$ ./bin/nosetests`

Run only environment-independent tests:
`$ ./bin/nosetests -a '!internal'`
