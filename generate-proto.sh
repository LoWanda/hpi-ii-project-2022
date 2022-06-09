#!/bin/bash

protoc --proto_path=proto --python_out=build/gen proto/bakdata/corporate/v2/corporate.proto
protoc --proto_path=proto --python_out=build/gen proto/bakdata/announcement/announcement.proto
protoc --proto_path=proto --python_out=build/gen proto/dpma/patent.proto
protoc --proto_path=proto --python_out=build/gen proto/dpma/v2/patent.proto
