ARAra Engine Repository
=====

이 저장소는 [ARA](https://ara.kaist.ac.kr/)의 서비스에 사용되는 Python BBS Application에 대한 저장소입니다. ARA 서비스는 [SPARCS](https://sparcs.org)에서 운영하고 있으며, SPARCS 관련 문의는 다음 메일 주소로 연락 바랍니다.

    staff at 5parc5.org ( replace 5 to s )

개발 환경 세팅하기
-----

*New(2019.07.23): [MIGRATION](MIGRATION.md)문서를 확인하세요.*

이 프로젝트는 Python Package 관리를 위해 Virtualenv를 사용하는 것을 권장합니다.

    $ sudo apt-get install python-pip
    $ sudo pip install virtualenv
    $ virtualenv env
    (env) $ pip install -r requirements.txt

이외에 추가로 thrift compiler가 필요합니다. 

    # On Debian Squeeze
    $ sudo add-apt-repository -y ppa:wnoronha/thrift
    $ sudo apt-get update
    $ sudo apt-get install thrift-compiler

혹은 [http://thrift.apache.org/](Apache Thrift-Home)에서 직접 받아 설치하셔도 됩니다.

이제 Arara Middleware Interface를 컴파일합니다.

    $ make

다음으로 Application을 Setting합니다. arara에서는 크게 `etc/arara_settings.py`와 `etc/warara_settings.py`를 사용합니다.
일반적으로는 다음 명령으로 자동으로 세팅할 수 있습니다:

    $ bin/devel_setup_script.sh
    
(실행 도중 적은 포트 번호 + 12) 가 웹서버의 포트 번호가 됩니다.
이제 개발 서버를 실행시켜 봅니다.

    $ python bin/warara_server.py -p (웹서버의 포트번호)
    
혹은 필요하다면 다음 명령으로 유닛 테스트를 실행해볼 수 있습니다.

    $ make test
    $ py.test arara/test (py.test가 설치되어 있는 경우)
    
DIRECT vs THRIFT
-----

ARARA 엔진은 django로 이루어진 프론트엔드와 python backend로 구성되어 있습니다.
두 모듈은 Middleware를 통해 통신하게 되고, 통신 방법에는 두 가지가 있습니다.

첫 번째는 thrift를 사용하는 것입니다. 이 모드를 사용하면 backend는 supervisord
데몬을 통해 별도로 구동하고, thrift가 둘 사이를 이어줍니다.

두 번째는 python middleware를 통해 직접 통신하는 것입니다. 이 방법을 사용하면
두 프로세스는 반드시 하나의 프로세스에서 동작하게 되지만, 서로간의 통신으로 인
한 overhead는 방지할 수 있습니다. 이 방법을 사용할 경우 Thrift는 Middleware로
오가는 데이터를 정규화하는 규격의 역할만 하게 되고, 실제로 RPC를 수행하지 않습니다.

현재 아라라 개발팀에서는 두 번째 방법을 권장하고 있으며, 이 문서에 있는 모든
내용은 두 번째 방법을 기준으로 쓰여진 것입니다.

첫 번째 방법을 사용하고자 할 경우 `etc/warara_settings`에서 연결 방법을 DIRECT 대신
THRIFT로 두면 됩니다.

Links
-----

<dl>
  <dt>ARA (Production)</dt>
  <dd>https://ara.kaist.ac.kr/</dd>
  <dt>Continuous Integration(Travis CI)</dt>
  <dd><a href="http://travis-ci.org/sparcs-kaist/arara/">http://travis-ci.org/sparcs-kaist/arara/ 
  <br/> <img src="https://secure.travis-ci.org/sparcs-kaist/arara.png?branch=master"></a></dd>
  <dt>SPARCS, developers' group in KAIST (Korea Advanced Institute of Science and Technology)</dt>
  <dd>https://sparcs.org</dd>
</dl>
