<!-- Página web da interface do médico -->
<!DOCTYPE html>
<html lang="pt-br">

<head>
  <meta charset="utf-8">
  <title>Monitorador de Pacientes</title>
  
  <!-- Bootstrap apenas para estilização da página html com css -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-KyZXEAg3QhqLMpG8r+8fhAXLRk2vvoC2f3B09zVXn8CA5QIVfZOJ3BCsw2P0p/We" crossorigin="anonymous">
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/js/bootstrap.bundle.min.js" integrity="sha384-U1DAWAznBHeqEIlVSCgzq+c9gqGAJn5c/t99JyeKa9xxaYpSvHU5awsuZVVFIhvj" crossorigin="anonymous"></script>

  <!-- JQuery para auxiliar com as funções Javascript -->
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>

  <!-- BootstrapTable para a formação mais otimizada da tabela -->
  <link href="https://unpkg.com/bootstrap-table@1.18.3/dist/bootstrap-table.min.css" rel="stylesheet">
  <script src="https://unpkg.com/bootstrap-table@1.18.3/dist/bootstrap-table.min.js"></script>

  <!-- Ícones usados(Refresh e Lixeira) -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" integrity="sha512-1ycn6IcaQQ40/MKBW2W4Rhis/DbILU74C1vSrLJxCq57o941Ym01SwNsOMqvEBFlcgUa6xLiPY/NS5R+E6ztJQ==" crossorigin="anonymous" referrerpolicy="no-referrer"/>
  <style>
    .bg-red {
      background-color: red;
    }

    tr:hover {
      background-color: blue;
    }
  </style>
</head>

<body class="bg-dark text-white">
  <div class="card-dark justify-content-center text-center table-responsive">

    <!-- Adicionar paciente -->
    <button onclick="add()">Adicionar</button>
    <hr>

    <!-- Tabela de pacientes -->
    <!-- <table id="table" class="text-white" data-row-style="rowStyle" data-show-refresh="true" data-ajax="ajaxRequest" data-sort-name="gravidade" data-sort-order="asc"> -->
    <table id="table" class="text-white" data-row-style="rowStyle" data-show-refresh="true" data-ajax="ajaxRequest" data-sort-order="desc" data-detail-view="true" data-detail-view-icon="false" data-detail-view-by-click="true" data-detail-formatter="detailFormatter">
      <thead>
        <tr>
          <th data-field="id">ID</th>
          <th data-field="usuario">Nome</th>
          <th data-field="temperatura" data-formatter="%s °C">Temperatura</th>
          <th data-field="fCardiaca" data-formatter="%s bat/min">Frequência Cardíaca</th>
          <th data-field="fRespiratoria" data-formatter="%s mov/min">Frequência Respiratória</th>
          <th data-field="oxigenacao" data-formatter="%s %">Oxigenação</th>
          <th data-field="pressao" data-formatter="%s mmHg">Pressão</th>
          <!-- <th data-field="gravidade" data-formatter="%s" data-sortable=true>Gravidade</th> -->
          <th data-field="operate" data-formatter="operateFormatter" data-events="operateEvents">Remover</th>
        </tr>
      </thead>
    </table>
    <script>
      //configura as funções a serem executadas na criação da tela
      $(document).ready(function() {
        //construção da tabela ordenando de acordo com o nível de oxigenação(pacientes com menor nível de oxigenação ficam no topo da tabela)
        $('#table').bootstrapTable({
          data: data,
          sortStable: true
        });

        //atualiza a tabela de pacientes a cada 10 segundos
        setInterval(function(){
          $('#table').bootstrapTable('refresh');
        }, 8000);
      });

      function detailFormatter(index, row) {
        var html = []
        $.each(row, function (key, value) {
          html.push('<p class="text-start"><b>' + key + ':</b> ' + value + '</p>')
        })
        return html.join('')
      }

      function add() {
        //construção do json para criar paciente
        let json = {
          method: 'add',
        }

        //transfere as informações no formato json para o backend(client), o qual se comunica com o servidor
        $.ajax({
          type: 'POST',
          dataType: 'json',
          url: 'client.php',
          async: true,
          data: json,
          success: function(response) {
            // console.log(response);

            //atualiza a tabela
            $('#table').bootstrapTable('refresh');
          },
          error: function(error) {
            alert('Erro: Servidor indisponível');
            console.log(error);
          }
        });
      }
      
      function ajaxRequest(params) {
        //construção do json para requisitar a lista de pacientes
        let json = {
          method: 'get',
        }

        //transfere as informações no formato json para o backend(client), o qual se comunica com o servidor
        $.ajax({
            method: 'POST',
            url: 'client.php',
            async: true,
            cache: false,
            data: json,
            success: function (response) {
              //padronização do json para formação da tabela
              response = JSON.parse(response);
              rows = JSON.parse(response.response.data);
              console.log(rows);
              
              //construção da tabela com inserção dos dados dos pacientes
              params.success({
                "rows": rows,
                "total": rows.length
              })
            },
            error: function (e) {
                console.log(e);
            }
        });
      }

      function operateFormatter(value, row, index) {
        //adiciona ícones de remover na tabela
        return [
          '<a class="remove" href="javascript:void(0)" title="Remove">',
          '<i class="fa fa-trash"></i>',
          '</a>'
        ].join('')
      }

      window.operateEvents = {
        'click .remove': function (e, value, row, index) {
          //construção do json de remoção de paciente
          let json = {
            method: 'delete',
            id: row.id
          }

          //transfere as informações no formato json para o backend(client), o qual se comunica com o servidor
          $.ajax({
            type: 'POST',
            dataType: 'json',
            url: 'client.php',
            async: true,
            data: json,
            success: function(response) {
              // console.log(response);
              
              //atualiza a tabela
              $('#table').bootstrapTable('refresh');
            },
            error: function(error) {
              console.log(error);
            }
          });
        }
      }

      //json genérico para criação da tabela
      var data = [{
          'id': null,
          'nome': null,
          'temperatura': null,
          'fCardiaca': null,
          'fRespiratoria': null,
          'oxigenacao': null,
          'pressao': null,
          'gravidade': null
        }
      ]

    //adiciona background vermelho aos pacientes em estado grave
    function rowStyle(row, index) {
      if (row.temperatura > 38.5 || row.fCardiaca > 110 || row.fRespiratoria > 20 || row.pressao < 81) {
        if (row.oxigenacao < 92)
          return {
            classes: 'bg-red'
          }
      }
      return {
      }
    }
  </script>
  </div>
</body>

</html>
