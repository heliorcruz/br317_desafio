# br317_desafio
Teste técnico – SOFTWARE

Exemplo de raspagem de dados públicos utilizando BeatifullSoup em Python.  
Os dados utilizados neste exemplo foram obtidos da página do senado https://www12.senado.leg.br/hpsenado  
O exemplo obtém os dados das atividades legislativas ex. Projeto de Lei, Medida Provisória, etc.  

Python versão 3.7.0  

Instalar as dependências: `pip install -r requirements.txt`  

Configurar parametros de busca no arquivo config.ini:
  
```
[DEFAULT]
 
  type = PLS
  year = 2018
  number = 
  key =     
  autor =   

```
  
O arquivo 'config.json' possui os exemplos dos tipos mais usados disponiveis para o 'type' no campo TYPES, o exemplo acima esta usando  
"PLS" : "PROJETO DE LEI DO SENADO" e ano "2018"  
  
A configuração de database é feita em [DATABASE] do arquivo config.ini  
  
Executar python script  
`python main.py`  

