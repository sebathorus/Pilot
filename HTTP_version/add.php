<?php

$date = new DateTime();
$date = $date->format("d-M-Y  h:i:s  ");

if(!empty($_POST["temp"]))
{
 $tempesp = "Temperature=";
 $line = ($_POST["temp"]);
 $line2 = substr($line,(strlen($line)-17));
 $mydatafile = "/var/www/html/datahist/" . $line2 . "_temphist.txt";
 $mydatafile2 = "/var/www/html/datainst/" . $line2 . "_tempinst.txt";
 echo $line;
 $tempesp .= $line;

 file_put_contents($mydatafile, $date, FILE_APPEND);
 file_put_contents($mydatafile, $tempesp, FILE_APPEND);
 file_put_contents($mydatafile, "\n", FILE_APPEND);

 file_put_contents($mydatafile2, $date);
 file_put_contents($mydatafile2, $tempesp);
}

echo $tempesp;
?>
