<!DOCTYPE html>
<html lang="en">
	<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Bios Upgrades</title>

	<link href="css/bootstrap.min.css" rel="stylesheet">
	<link href="css/bootstrap-table.css" rel="stylesheet">
	<style>
	body {
		background: #eee;
	}
	</style>
	</head>

	<body>
	
<nav class="navbar navbar-inverse">
  <div class="container-fluid">
    <div class="navbar-header">
      <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
        <span class="sr-only">Toggle navigation</span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a class="navbar-brand" href="#">BIOS Upgrades</a>
    </div>

    <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
      <ul class="nav navbar-nav">
        <li class="active"><a href="#">Update Overview<span class="sr-only">(current)</span></a></li>
        <li><a href="log.php">Activity Log</a></li>
	<li><a href=".">Folder listing</a></li>
      </ul>
    </div><!-- /.navbar-collapse -->
  </div><!-- /.container-fluid -->
</nav>

	<div class="container" >
		<div class="row">
		<div class="col-md-12">
			<table class="table table-condensed table-responsive table-striped" data-url="results.json" data-toggle="table" data-search="true" data-pagination="true" data-page-size="80">
    				<thead>
					<tr>
						<th colspan="3">
						Last check:
						<?php
							if (file_exists("results.json")) 
								echo date("d. F Y H:i:s", filemtime("results.json"));
						?>
						</th>
					</tr>
					<tr>
            					<th data-sortable="true" data-field="system_id">System ID</th>
            					<th data-formatter="bios_formatter" data-field="current_bios">Current BIOS</th>
            					<th data-sortable="true" data-field="last_changed" data-sorter="day_sorter">Last changed</th>
        				</tr>
    				</thead>
			</table>



		</div>
		</div>
	</div>

	<script src="js/jquery.min.js"></script>
	<script src="js/bootstrap.min.js"></script>
	<script src="js/bootstrap-table.js"></script>
	<script src="js/bootstrap-table-en-US.js"></script>
	<script type="text/javascript">
		function bios_formatter(value, row) {
			return '<a href="' + row["file_name"] + '">' + value + '</a>';
    		}

		function day_sorter(a, b) {
			var dateA = a.split(" ")[0].split(".");
			var dateB = b.split(" ")[0].split(".");
			var x = new Date(dateA[2], (dateA[1] - 1), dateA[0]);
			var y = new Date(dateB[2], (dateB[1] - 1), dateB[0]);
			return y-x;
		}
	</script>
	</body>

</html>

	
