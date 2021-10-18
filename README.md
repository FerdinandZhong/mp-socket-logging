# Serving

Batch inference serving framework built for deep learning models.

This library provides the network service layer for machine learning models.

The full document can be found in :notebook: [GitLab Pages](https://shopee-ds.git-pages.garena.com/ml-platform/model-serving/dserving).

:paperclip: [MLP Sharing Slides](https://docs.google.com/presentation/d/127SY0HX5yMv9piLniRQDS56ZWOvFvhjd4ESK6Dbsncg/edit?usp=sharing)

:paperclip: [DS Sharing Slides](https://docs.google.com/presentation/d/1-2AG8jp9Nvh8KBFtjtjolVc1BpNY1dmF4UzJLAC1qHU/edit?usp=sharing)

### Features

* HTTP service
* supports all kind of model frameworks
* dynamic batching for requests
* pipeline for (pre, inf, post)
* request & response data validation
* graceful shutdown
* health check
* warmup
* monitoring metrics
* basic authentication
* OpenAPI spec
* high/low priority requests with different timeout

## Usage

* Install the latest stable version from [Garena PyPI]: `pip install --extra-index-url https://pypi.garenanow.com/ dserving`
  * If you want to try the pre-release version, check [Garena PyPI]: `pip install --extra-index-url https://pypi.garenanow.com/ dserving=={version}`
* Run one of the [examples](examples): `python examples/demo.py`.
* Test the API: `http :8080 duration:=0` (you may need to install `pip install httpie`)
* Learn about the arguments: `python examples/demo.py --help`
* Generate the OpenAPI spec: `python example/demo.py --openapi > openapi.json`

[Garena PyPI]: https://pypi.garenanow.com/simple/dserving/

## Interface

To use this library, the user needs to provide a Python class that contains:

* model loading (all kinds of frameworks)
* model inference
* preprocessing & postprocessing (optional, this part will run in parallel)
* request & response data schema


### SPEX with DServing

Please refer to the following repo for further guidance.

https://git.garena.com/shopee-ds/ml-platform/model-serving/dserving-demos
