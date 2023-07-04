#!/bin/bash

src_dir=$(dirname -- ${BASH_SOURCE[0]});
cd $src_dir

CC="gcc"
CFLAGS="-g -Wall -Wextra"
SRCS="sockapi.c socklib.c dispatcher.s"
OUTPUT="sockapi"

$CC $CFLAGS $SRCS -o $OUTPUT
