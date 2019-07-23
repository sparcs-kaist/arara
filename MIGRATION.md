# ARAra Engine Migration from Debian:Squeeze to Ubuntu 18.04

최소한의 Maintenance 협업이 가능하도록 Production code 와 저장소, 최신 개발환경간에 필요한 최소한의 동기화를 진행중입니다.

## Docker

* Dockerfile
  * docker/Dockerfile 생성. 다음 커맨드로 최소한의 실행이 가능합니다.
    $ docker pull redis
    $ docker run --name redis-something -d -p 6379:6379 redis
    $ docker build -t arara-engine-image -f docker/Dockerfile .

## TODO

* Python 2 -> 3 Migration
