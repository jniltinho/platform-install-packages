## Purpose

Garantir que os pacotes `.deb` do Kaltura CE Rigel-18.20.0 para Ubuntu 24.04 (noble) possam ser gerados de forma reprodutível, a partir de fontes publicamente resolvíveis, em uma VM limpa.

## ADDED Requirements

### Requirement: Build repetível em VM limpa
O build SHALL gerar todos os `.deb` do conjunto All-In-One a partir de uma VM Ubuntu 24.04 limpa (box `bento/ubuntu-24.04` fixada no Vagrantfile), com um único comando e sem intervenção manual. "Repetível" significa repetibilidade funcional: dois builds limpos produzem o mesmo conjunto de pacotes e versões. Não é reprodutibilidade bit a bit.

O conjunto All-In-One é: `kaltura-postinst`, `kaltura-base`, `kaltura-front`, `kaltura-batch`, `kaltura-db`, `kaltura-server`, `kaltura-ffmpeg`, `kaltura-ffmpeg-aux`, `kaltura-sphinx`, `kaltura-nginx`, `kaltura-elasticsearch`, `kaltura-kmcng`, `kaltura-html5lib`, `kaltura-html5lib3`, `kaltura-html5-studio`, `kaltura-html5-studio3`, `kaltura-html5-analytics`.

#### Scenario: Build completo
- **WHEN** o operador executa `vagrant up build` em `deb/noble/`
- **THEN** o provisionamento termina com código 0
- **AND** existe um `.deb` para cada pacote do conjunto All-In-One em `deb/noble/repo/`

#### Scenario: Falha de pacote interrompe o build
- **WHEN** a construção de qualquer pacote do conjunto falha
- **THEN** o build termina com código diferente de 0 e informa qual pacote falhou

### Requirement: Versões alinhadas ao RPM 18.20.0
Os pacotes do core (`kaltura-base`, `kaltura-front`, `kaltura-batch`, `kaltura-db`, `kaltura-server`) SHALL ter a versão `18.20.0` e embutir o código do servidor Kaltura do commit `29cf45469c1e210498087942f5b76b5c706e4cda` (tag `Rigel-18.20.0-rel`, cujo `VERSION.txt` é `Rigel-18.20.0`).

#### Scenario: Versão do core
- **WHEN** se inspeciona `dpkg-deb -f kaltura-base_*.deb Version`
- **THEN** o valor começa com `18.20.0`

### Requirement: Fontes resolvíveis
Toda fonte usada pelo build SHALL ser baixável de uma URL pública. Quando a origem original de uma fonte deixa de existir, a URL dessa fonte SHALL ser substituída de forma permanente por um espelho controlado pelo projeto (assets de Release do GitHub do próprio repositório), publicado junto com o SHA-256. Não há fallback em tempo de build: cada fonte tem uma única URL.

#### Scenario: Fonte espelhada
- **WHEN** o build baixa o código do servidor
- **THEN** a URL usada é a do espelho do projeto
- **AND** o SHA-256 do arquivo baixado confere com o publicado no espelho, senão o build falha

### Requirement: Repositório apt local
O build SHALL publicar os `.deb` gerados como repositório apt consumível via `deb [trusted=yes] file:<dir> ./`.

#### Scenario: Índice do repositório
- **WHEN** o build termina
- **THEN** `deb/noble/repo/Packages.gz` existe e lista todos os pacotes gerados

### Requirement: Qualidade dos pacotes
Cada `.deb` gerado SHALL instalar em Ubuntu 24.04 sem dependências insatisfeitas, usando apenas os repositórios da distro (main/universe/multiverse), o PPA `ondrej/php`, o repositório apt da Elastic 7.x (versão 7.17) e o repositório local.

#### Scenario: Resolução de dependências
- **WHEN** se executa `apt-get install --simulate kaltura-server` com esses repositórios configurados
- **THEN** o apt resolve todas as dependências sem erro
