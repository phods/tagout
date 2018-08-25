#!/bin/bash

#Modificado por joão bosco 09/01/2016
#Script para verificar se determinados processos estão em execução no sistema.
#Os processos a serem monitorados devem ser passados como parâmetro no momento de execução deste script, entre aspas e separados por espaço.
#Por exemplo:
#./novolog.sh "close.py"

#Verifica se o arquivo temporário existe e o remove.
while :

do

if [ -e /tmp/processos.tmp ]; then
rm /tmp/processos.tmp
fi
PROCESSO=tagou11.py
INTERVALO=3
#Cria os diretórios para armazenamento do log

#mkdir /home/share/$(date +%Y)

#mkdir /home/share/$(date +%Y)/$(date +%m)

#Executa para cada processo passado como parâmetro.
for i in "$PROCESSO"; do

   #Executa o comando ps para todos os usuários e filtra com o grep o processo monitorado, depois são executados filtros inversos para excluir
   #aparições da execução do próprio grep e do nosso script. O resultado, se existir, é salvo em um arquivo temporário.
   ps aux | grep "$i" | grep -v "grep" | grep -v "novolog.sh" > /tmp/processos.tmp

   #Calcula-se o número de linhas do arquivo criado acima e atribui esse valor à variável A.
   A=$(wc -l /tmp/processos.tmp | awk '{print $1}')
   
   #Se A é maior ou igual a 1 significa que o processo está em execução,
   #então é salva uma linha contendo um OK para o processo monitorado naquele momento.
   #Senão é salvo um ERRO no log e tembém é enviado um email para o administrador do sistema avisando do ocorrido.
   if [ $A -ge 1 ]; then
     echo $PROCESSO run 
     #echo -e "$i\tOK\t$(date +"%x\t%X")" >> /home/share/$(date +%Y)/$(date +%m)/$(date +%d).log
   else
      echo -e "$i\tERRO\t$(date +"%x\t%X")" >> /home/share/$(date +%Y)/$(date +%m)/$(date +%d).log
      mysql --host=localhost --user=root --password=toor test_log_bosc <<EOF
      insert into log (descr) value("Programa interrompido")
EOF
      echo -e "\nPor algum motivo inesperado o processo $i não está sendo executado neste momento." #| mutt -s "[ALERTA] Problemas com $i em $(date +"%x  %X")" email@dominio.com.br -a  /tmp/processos.tmp
      echo -e "\Reiniciando o processo..."
      sudo python /home/pi/pasta_teste/tagou11.py
      sleep $INTERVALO
      mysql --host=localhost --user=root --password=toor test_log_bosc <<EOF
      insert into log (descr) value("Programa reiniciado!")
EOF
   fi
   
done

done
