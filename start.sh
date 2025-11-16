#!/bin/bash

pushd src

uvicorn app:app --reload --host 0.0.0.0 --port 8081 --reload

popd