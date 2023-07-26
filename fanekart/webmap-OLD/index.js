

var mindato = function( dateObj) { 

	var monthNames = [
			"jan", "feb", "mar",
			"apr", "mai", "juni", "juli",
			"aug", "sep", "okt",
			"nov", "des"
		];

		
	var datostreng = dateObj.getDate() + ". " 
						+ monthNames[dateObj.getMonth()] + " " 
						+  dateObj.getFullYear();

	var helTime = ('0'+dateObj.getHours()).slice(-2);
	var minutt = ('0'+dateObj.getMinutes()).slice(-2);
	var sekund = ('0'+dateObj.getSeconds()).slice(-2);

	var klokkestreng = helTime + ':' + minutt + ':' + sekund; 

	return { dato: datostreng, klokke: klokkestreng }; 

}



var map = new L.map('map').setView([63.43, 10.40], 14);


L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

function onLocationFound(e) {
	var radius = e.accuracy / 2;

	L.marker(e.latlng).addTo(map)
		.bindPopup("Du er her!");

	L.circle(e.latlng, radius).addTo(map)
		.bindPopup("Usikkerhet");
}

function onLocationError(e) {
	alert(e.message);
}

map.on('locationfound', onLocationFound);
map.on('locationerror', onLocationError);

/*
map.locate({setView: true, maxZoom: 13}); 
*/

realtime = L.realtime({
        url: 'https://jansimple.pythonanywhere.com/getfile/Jan.geojson',
        // url: 'https://jansimple.pythonanywhere.com/getfile/SSMfane.geojson',
        // url: 'https://jansimple.pythonanywhere.com/getfile/SSMfaneX.geojson',
        // url: 'https://jansimple.pythonanywhere.com/getfile/Jan.geojson',
        crossOrigin: true,
        type: 'json'
    },
	{
        interval: 30 * 1000, 
		pointToLayer: function (feature, latlng) {
			return L.marker(latlng, {
				'icon': L.icon({
					iconUrl: 'http://labs.ltglahn.no/kart/gps/img/1431044506_circle_red36x36.png',
					iconSize:     [36, 36], // size of the icon
					iconAnchor: [18, 18], 
					popupAnchor:  [0, 0] // point from which the popup should open relative to the iconAnchor
				})
			});
		}
	}).addTo(map);



realtimeLinje = L.realtime({
        url: 'https://jansimple.pythonanywhere.com/getfile/Jan_kurve.geojson',
        // url: 'https://jansimple.pythonanywhere.com/getfile/SSMfane_kurve.geojson',
        // url: 'https://jansimple.pythonanywhere.com/getfile/SSMfane_kurveX.geojson',
        // url: 'https://jansimple.pythonanywhere.com/getfile/Jan_kurve.geojson',
        crossOrigin: true,
        type: 'json'
    },
	{
        interval: 30 * 1000
    }
	).addTo(map);

var firstTimeLinje = true; 


	
realtimeLinje.on('update', function(e) {

	if (firstTimeLinje) {
	   popupContent = function(fId) {
				return 'Spor etter SSM fana'; 
			},
		bindFeaturePopup = function(fId) {
			realtimeLinje.getLayer(fId).bindPopup(popupContent(fId));
		},

		Object.keys(e.enter).forEach(bindFeaturePopup);
		Object.keys(e.update).forEach(updateFeaturePopup);
	}
	
	firstTimeLinje = false; 

});


var punkt = {"type": "FeatureCollection",
"features": [{ "type": "Feature", 
"properties": { "description": "Vi spiller  på Persaunet Helse- og Velferdssenter. Etterpå serverer de saft.", 
"name": "Persaunet Helse- og Velferdssenter" }, "geometry": { "type": "Point", "coordinates": [ 10.438772163518735, 63.428913977547886 ] } }]};


// 17. mai punkt 
/* 
{"type": "FeatureCollection", "features": [
	{"type":"Feature","geometry":{"type":"Point","coordinates":[10.455251,63.433514]},"properties":{"cartodb_id":5,"name":"Strindheim&nbsp;skole","description":"07:30 Oppmøte ALLE<br>\nFlaggheis, taler, allsang, korpsmusikk, avmarsj mot sentrum (4-7 trinn) kl 08:05<br>\n<em>Ettermiddag:</em><br>\nCa 17:00 korpset ankommer, festen begynner","created_at":"2014-05-16T21:14:53Z","updated_at":"2015-05-06T15:46:44Z"}},
	{"type":"Feature","geometry":{"type":"Point","coordinates":[10.455691,63.428077]},"properties":{"cartodb_id":7,"name":"Bromstad&nbsp;h&vf.sent.","description":"Vi stopper på Bromstad Helse- og velferdssenter  for å spille litt","created_at":"2014-05-16T21:56:39Z","updated_at":"2014-05-16T21:57:09Z"}},
	{"type":"Feature","geometry":{"type":"Point","coordinates":[10.444608,63.4244]},"properties":{"cartodb_id":2,"name":"Valentinlyst&nbsp;16:00","description":"16:00 - oppmøte ALLE, P-plass ved Valentinlyst sykehjem. ","created_at":"2014-05-16T19:25:51Z","updated_at":"2015-05-06T15:48:20Z"}},
	{"type":"Feature","geometry":{"type":"Point","coordinates":[10.41294,63.43262]},"properties":{"cartodb_id":1,"name":"Thornæsparken","description":"Korpset marsjerer hit fra skolen (4. trinn og oppover). 2. og 3. trinn møter senest 08:45. Avmarsj Bispegata 09:00","created_at":"2014-05-16T19:22:28Z","updated_at":"2015-05-06T15:48:52Z"}},
	{"type":"Feature","geometry":{"type":"Point","coordinates":[10.398731,63.427857]},"properties":{"cartodb_id":4,"name":"Bispegata","description":"Korpset marsjerer hit for å slutte seg til resten av barnetoget. Avmarsj 10:00","created_at":"2014-05-16T19:44:02Z","updated_at":"2015-05-06T15:59:07Z"}},
	{"type":"Feature","geometry":{"type":"Point","coordinates":[10.441668,63.425029]},"properties":{"cartodb_id":8,"name":"Valentinlyst&nbsp;06:00","description":"HK møter 06:00 på parkeringsplassen Valentinlyst, mot kirka. ","created_at":"2015-05-04T15:55:49Z","updated_at":"2015-05-06T18:01:27Z"}}
]} 
*/

var henteomraade = {"type": "FeatureCollection", "features": [
	{"type":"Feature","geometry":{"type":"MultiPolygon","coordinates":[[[[10.40004,63.428514],[10.400142,63.428422],[10.400335,63.428437],[10.400442,63.428528],[10.400534,63.428691],[10.400909,63.429183],[10.401328,63.429656],[10.401607,63.430025],[10.401843,63.430496],[10.402519,63.431311],[10.402958,63.431791],[10.403205,63.43217],[10.403452,63.432588],[10.403624,63.432832],[10.403699,63.433015],[10.403398,63.432991],[10.403205,63.432856],[10.403044,63.432477],[10.402604,63.431945],[10.402014,63.431249],[10.401392,63.430553],[10.400952,63.429934],[10.400641,63.429445],[10.400426,63.429065],[10.400228,63.428806],[10.40004,63.428514]]]]},"properties":{"cartodb_id":1,"name":"Henteområde","description":"Sånn cirka i dette området går toget i oppløsning -- det er her du må plukke opp ungene dine!","created_at":"2015-04-29T22:01:42Z","updated_at":"2015-04-29T22:12:28Z"}}]}; 


var marsjgeo = {"type": "FeatureCollection",
"features": [{ "type": "Feature", "properties": { "description": "Marsrute 1. Mai. Vi spiller og pauser på Persaunet Helse- og Velferdssenter", "name": "Marsjrute 1. Mai" }, "geometry": { "type": "MultiLineString", "coordinates": [ [ [ 10.454849651765914, 63.43347910933781 ], [ 10.455133849727513, 63.433901568279303 ], [ 10.455439230583663, 63.434682332235496 ], [ 10.454170047384643, 63.43490525813835 ], [ 10.454746, 63.43527 ], [ 10.454864, 63.435368 ], [ 10.454966, 63.435445 ], [ 10.453094, 63.435683 ], [ 10.451244, 63.435901 ], [ 10.450621, 63.435954 ], [ 10.449414, 63.436028 ], [ 10.449092, 63.435145 ], [ 10.448738, 63.43421 ], [ 10.448492, 63.433576 ], [ 10.448481, 63.433495 ], [ 10.44862, 63.433327 ], [ 10.44714, 63.432813 ], [ 10.446464, 63.433178 ], [ 10.444576, 63.432549 ], [ 10.443803, 63.433125 ], [ 10.441609129136143, 63.432619738170764 ], [ 10.440686387039305, 63.432161214816539 ], [ 10.440021094111204, 63.431903882028401 ], [ 10.439544, 63.431436 ], [ 10.439225924269126, 63.431063884367184 ], [ 10.439317397668015, 63.430955060205484 ], [ 10.438856420929257, 63.430789641372897 ], [ 10.438430192462119, 63.430587525387466 ], [ 10.438128, 63.430328 ], [ 10.437849, 63.430064 ], [ 10.437707186590458, 63.429828613313511 ], [ 10.437537, 63.429622 ], [ 10.437312, 63.429459 ], [ 10.437001, 63.429291 ], [ 10.436282, 63.429075 ], [ 10.435809704251394, 63.42894887576449 ], [ 10.435870157505946, 63.428788572039785 ], [ 10.435832, 63.428398 ], [ 10.436035, 63.42811 ], [ 10.436281431753009, 63.427957264241819 ], [ 10.438559148198154, 63.428197514763625 ], [ 10.440833605695945, 63.428406921773011 ], [ 10.441413020912364, 63.429207466003945 ], [ 10.442261652792947, 63.429463689767545 ], [ 10.44375087662563, 63.429721851640501 ], [ 10.444954801339669, 63.430295942568875 ], [ 10.445858898591952, 63.430628939077891 ], [ 10.447560797247812, 63.430972829440925 ], [ 10.448591065191625, 63.431446638652353 ], [ 10.448998359790195, 63.431584135088805 ], [ 10.449146053371603, 63.431583353647476 ], [ 10.449316883270939, 63.431633320731223 ], [ 10.44935347343182, 63.431705638416176 ], [ 10.44957160634795, 63.431915680633374 ], [ 10.450559047449342, 63.432925459620705 ], [ 10.450176110214342, 63.433692520496514 ], [ 10.451447533963657, 63.433980901725398 ], [ 10.452854603852995, 63.434398518023848 ], [ 10.453595456226443, 63.434607035986218 ], [ 10.454096431184125, 63.434266960432318 ], [ 10.454715160626318, 63.433923205786215 ], [ 10.454765196809836, 63.433509668059024 ] ] ] } }]};



// Marsjruter for 17. mai 
/* 
{"type": "FeatureCollection", "features": [
	{"type":"Feature","geometry":{"type":"MultiLineString","coordinates":[[[10.442065,63.425214],[10.44228,63.425219],[10.442993,63.425192],[10.443234,63.425264],[10.443841,63.425531],[10.444597,63.425922],[10.445455,63.426306],[10.446169,63.426553],[10.446399,63.426637],[10.446576,63.426548],[10.446786,63.426462],[10.447134,63.42663],[10.447606,63.426846],[10.448245,63.427155],[10.448642,63.427304],[10.448851,63.427414],[10.449028,63.427494],[10.449141,63.427566],[10.449176,63.427662],[10.44921,63.427758],[10.449237,63.427971],[10.449286,63.428036],[10.449436,63.42811],[10.44979,63.428242],[10.450133,63.428415],[10.45068,63.428657],[10.450847,63.428744],[10.451147,63.428869],[10.451571,63.429039],[10.45178,63.429181],[10.451882,63.429296],[10.452054,63.429399],[10.452343,63.429555],[10.451989,63.42967],[10.451539,63.4298],[10.451469,63.42997],[10.451565,63.430032],[10.451581,63.430121],[10.45163,63.43016],[10.451903,63.430193],[10.452424,63.430248],[10.452837,63.43027],[10.453137,63.43027],[10.453572,63.430263],[10.454006,63.430236],[10.454274,63.43021],[10.454387,63.4302],[10.454425,63.430133],[10.454516,63.430092],[10.454671,63.43009],[10.454779,63.430114],[10.454789,63.430181],[10.454725,63.430241],[10.454655,63.430308],[10.454741,63.430448],[10.455111,63.431247],[10.45517,63.431378],[10.455546,63.43229],[10.455626,63.432494],[10.455862,63.432919],[10.455723,63.432945],[10.455025,63.433039],[10.454527,63.433118],[10.454543,63.4332],[10.454714,63.433399],[10.45494,63.433545],[10.45517,63.433567],[10.45517,63.433567]]]},"properties":{"_cartodb_id0":1,"name":"SSM marsj morgen","description":"SSM marsjrute morgen 17.Mai","created_at":"2015-04-29T22:56:39Z","updated_at":"2015-05-05T20:21:42Z","timestamp":null,"begin":null,"_end":null,"altitudemode":null,"tessellate":null,"extrude":null,"visibility":null,"draworder":null,"icon":null,"cartodb_id":1,"myid":1}},
	{"type":"Feature","geometry":{"type":"MultiLineString","coordinates":[[[10.444608,63.4244],[10.444071,63.424496],[10.4442,63.424909],[10.445788,63.424871],[10.448663,63.424852],[10.450938,63.424852],[10.45127,63.424914],[10.451646,63.425092],[10.452161,63.425312],[10.452375,63.425427],[10.452569,63.425485],[10.453202,63.425615],[10.453835,63.425735],[10.454113,63.425792],[10.454371,63.425879],[10.454446,63.425989],[10.454446,63.426167],[10.454049,63.426714],[10.453749,63.427141],[10.453631,63.427299],[10.453599,63.427482],[10.453609,63.427611],[10.453856,63.427645],[10.454013,63.42784],[10.454448,63.427984],[10.454734,63.428187],[10.454865,63.428325],[10.455428,63.428169],[10.455453,63.42821],[10.454816,63.428386],[10.454848,63.428552],[10.455045,63.428754],[10.455128,63.428839],[10.454765,63.428952],[10.454478,63.429172],[10.454347,63.429373],[10.454448,63.4297],[10.454513,63.429922],[10.454583,63.430053],[10.454642,63.430058],[10.454744,63.430076],[10.454838,63.430123],[10.454856,63.430177],[10.454823,63.430221],[10.454634,63.43025],[10.454527,63.430248],[10.454486,63.430232],[10.454457,63.430209],[10.454425,63.430178],[10.454425,63.430146],[10.454462,63.430106],[10.454529,63.430083],[10.454623,63.430073],[10.454763,63.430101],[10.454816,63.430155],[10.454771,63.430216],[10.454696,63.430252],[10.454685,63.430275],[10.454784,63.430475],[10.454899,63.430711],[10.455064,63.431032],[10.455133,63.43118],[10.455189,63.43129],[10.455346,63.431634],[10.455445,63.431896],[10.455551,63.432093],[10.455745,63.432557],[10.455843,63.432767],[10.455899,63.43289],[10.455917,63.432922],[10.455693,63.432946],[10.455686,63.432946],[10.455387,63.432992],[10.455068,63.433024],[10.45489,63.433058],[10.454698,63.433078],[10.454534,63.433115],[10.454506,63.433168],[10.45456,63.433225],[10.454607,63.433285],[10.45465,63.433343],[10.454724,63.433408],[10.454866,63.433496],[10.454969,63.433587],[10.455036,63.433713]]]},"properties":{"_cartodb_id0":1,"name":"SSM marsj ettermiddag","description":"Marsjrute for SSM 17. Mai ettermiddag.","created_at":"2014-05-16T18:22:06Z","updated_at":"2015-05-05T20:21:51Z","timestamp":null,"begin":null,"_end":null,"altitudemode":null,"tessellate":-1,"extrude":-1,"visibility":-1,"draworder":null,"icon":null,"cartodb_id":3,"myid":3}},
	{"type":"Feature","geometry":{"type":"MultiLineString","coordinates":[[[10.455149,63.433643],[10.455198,63.433742],[10.455089,63.433798],[10.454908,63.433851],[10.454691,63.433931],[10.454486,63.434042],[10.454463,63.434054],[10.454297,63.434162],[10.454079,63.434281],[10.453863,63.434416],[10.453705,63.434523],[10.453642,63.434575],[10.453794,63.434641],[10.453953,63.434709],[10.454101,63.434804],[10.454209,63.434882],[10.454214,63.434895],[10.454386,63.435006],[10.454388,63.435012],[10.454632,63.435147],[10.454777,63.435227],[10.45492,63.435336],[10.454945,63.435398],[10.454882,63.435455],[10.454739,63.435486],[10.454543,63.435509],[10.454268,63.435537],[10.454036,63.435568],[10.453823,63.435598],[10.453467,63.435652],[10.453159,63.43569],[10.452661,63.435736],[10.45215,63.435793],[10.451773,63.435851],[10.451377,63.435893],[10.451165,63.43592],[10.450914,63.435937],[10.450464,63.435977],[10.45004,63.436],[10.449473,63.436031],[10.449027,63.436066],[10.448735,63.436083],[10.448467,63.436108],[10.448115,63.436131],[10.447426,63.436183],[10.446609,63.436269],[10.446219,63.436302],[10.445607,63.436359],[10.445221,63.436403],[10.444836,63.436432],[10.444466,63.436458],[10.444252,63.436476],[10.443868,63.436502],[10.443565,63.436525],[10.443167,63.436568],[10.44284,63.436602],[10.442584,63.43664],[10.442231,63.436695],[10.441795,63.436757],[10.441557,63.436789],[10.441295,63.43683],[10.441003,63.436884],[10.440789,63.436927],[10.440568,63.43699],[10.440288,63.43705],[10.440073,63.437084],[10.439778,63.43712],[10.439528,63.437132],[10.439244,63.43715],[10.438859,63.437142],[10.43858,63.437131],[10.438312,63.4371],[10.437942,63.43711],[10.437715,63.437078],[10.4376,63.437013],[10.43745,63.436917],[10.43725,63.436817],[10.437068,63.436722],[10.436881,63.436631],[10.436696,63.436542],[10.436468,63.43646],[10.436175,63.436403],[10.435821,63.436365],[10.435444,63.436338],[10.435313,63.436322],[10.435179,63.436314],[10.435065,63.436337],[10.434914,63.43634],[10.4349,63.436338],[10.43474,63.436337],[10.434391,63.436339],[10.433789,63.436284],[10.433247,63.436258],[10.432641,63.436228],[10.432197,63.4362],[10.431874,63.43619],[10.431508,63.436178],[10.431263,63.436166],[10.43103,63.436188],[10.430863,63.436182],[10.430731,63.436156],[10.430623,63.43606],[10.430459,63.435962],[10.430304,63.435941],[10.430125,63.435975],[10.429956,63.436023],[10.429847,63.43604],[10.429702,63.436057],[10.429178,63.436027],[10.429164,63.436027],[10.428715,63.436004],[10.42837,63.435977],[10.427885,63.435951],[10.427439,63.435919],[10.427038,63.435903],[10.426625,63.435884],[10.426251,63.435865],[10.425896,63.435853],[10.425625,63.435829],[10.425511,63.435795],[10.425409,63.435732],[10.425232,63.435678],[10.424931,63.435621],[10.424611,63.435597],[10.424312,63.43556],[10.42404,63.435527],[10.423921,63.43548],[10.423907,63.4354],[10.423955,63.435227],[10.423979,63.435075],[10.423982,63.434979],[10.423864,63.434938],[10.423641,63.434929],[10.422674,63.434913],[10.422288,63.434907],[10.422148,63.434912],[10.422022,63.434916],[10.421871,63.434937],[10.421754,63.434935],[10.4216,63.434919],[10.421377,63.434909],[10.421184,63.4349],[10.420899,63.434908],[10.420705,63.434912],[10.420421,63.434914],[10.419967,63.434944],[10.419554,63.434964],[10.419221,63.434813],[10.418976,63.434717],[10.418733,63.434594],[10.418503,63.434501],[10.418295,63.434398],[10.417993,63.434281],[10.41772,63.434177],[10.417555,63.434115],[10.417419,63.434133],[10.417397,63.434136],[10.417233,63.434206],[10.417097,63.434285],[10.416736,63.434463],[10.416581,63.43455],[10.41646,63.434535],[10.416343,63.434489],[10.416196,63.434438],[10.416023,63.434358],[10.415647,63.434197],[10.415282,63.434039],[10.41507,63.433955],[10.414675,63.433797],[10.414235,63.433604],[10.413745,63.433414],[10.413362,63.433271],[10.412945,63.433082],[10.412302,63.432832]]]},"properties":{"_cartodb_id0":1,"name":"SSM marsj formiddag","description":"Marsjrute om formiddagen 17. Mai fra skolen til Thornæsparken.","created_at":"2014-05-16T19:18:28Z","updated_at":"2015-05-05T20:21:47Z","timestamp":"2014-05-16T22:41:07Z","begin":"2014-05-16T22:41:07Z","_end":"2014-05-16T22:41:06Z","altitudemode":null,"tessellate":1,"extrude":-1,"visibility":-1,"draworder":null,"icon":null,"cartodb_id":2,"myid":2}},
	{"type":"Feature","geometry":{"type":"MultiLineString","coordinates":[[[10.412255,63.432806],[10.412046,63.432724],[10.411187,63.432384],[10.41042,63.432084],[10.409546,63.431729],[10.407647,63.430915],[10.407287,63.430764],[10.407207,63.430671],[10.4071,63.430591],[10.40688,63.43044],[10.406821,63.430368],[10.406553,63.43033],[10.406188,63.430356],[10.406011,63.430378],[10.405855,63.430287],[10.405367,63.429996],[10.404825,63.42974],[10.403833,63.429341],[10.403355,63.428842],[10.403189,63.428672],[10.402953,63.428072],[10.401499,63.42823],[10.400051,63.428379],[10.399997,63.428221],[10.399863,63.427966],[10.399606,63.427894],[10.398833,63.427854]]]},"properties":{"_cartodb_id0":null,"name":"SSM marsj formiddag #2","description":"Marsjrute formiddag 17. Mai fra Thornæsparken til Bispegata","created_at":"2015-05-06T15:56:53Z","updated_at":"2015-05-06T16:01:11Z","timestamp":null,"begin":null,"_end":null,"altitudemode":null,"tessellate":null,"extrude":null,"visibility":null,"draworder":null,"icon":null,"cartodb_id":4,"myid":4}},
	{"type":"Feature","geometry":{"type":"MultiLineString","coordinates":[[[10.39872,63.427846],[10.396564,63.427717],[10.396188,63.428384],[10.395942,63.428797],[10.395502,63.429617],[10.395051,63.430462],[10.394236,63.431959],[10.393506,63.433197],[10.395759,63.43324],[10.397294,63.433269],[10.39739,63.432727],[10.397476,63.431954],[10.397669,63.430951],[10.397787,63.43039],[10.399278,63.430328],[10.400083,63.430318],[10.401392,63.430256],[10.401392,63.430256],[10.401392,63.430256]]]},"properties":{"_cartodb_id0":null,"name":"Barnetog sentrum","description":"Marsjrute barnetog i sentrum. Bispegt – Munkegt – Olav Trygvassons gt - Nordre gt - Kongens gt – Kjøpmanns gate ","created_at":"2015-05-06T20:42:09Z","updated_at":"2015-05-07T04:39:39Z","timestamp":null,"begin":null,"_end":null,"altitudemode":null,"tessellate":null,"extrude":null,"visibility":null,"draworder":null,"icon":null,"cartodb_id":5,"myid":5}}
]}; 

// Henteområde 17. mai 
henteomr =  L.geoJson(henteomraade, {
		style: function(feature) {
         return {
			color: '#000', 
			fillColor: 'blue',
			weight: 4,
			opacity: .75,
			
		};
		}, 
			onEachFeature: function (feature, layer) {
				layer.bindPopup(feature.properties.description);
			}
			})	.addTo(map);

label = new L.Label()
label.setContent('Henteområde<br>etter barnetoget')
label.setLatLng(henteomr.getBounds().getCenter())
map.showLabel(label);


*/

marsjering =  L.geoJson(marsjgeo, {
		style: function(feature) {
         return {
			color: "#ff0000"
		};
		}, 
			onEachFeature: function (feature, layer) {
				layer.bindPopup(feature.properties.description);
			}
			}).addTo(map);


	
viktigePunkt = L.geoJson(punkt, {
			onEachFeature: function (feature, layer) {
				layer.bindPopup('<b>' + feature.properties.name + '</b><br>' +  feature.properties.description);
			}, 
			pointToLayer: function (feature, latlng) {
				return L.circleMarker(latlng, {
					radius: 8,
					fillColor: "#ff7800",
					color: "#000",
					weight: 1,
					opacity: 1,
					fillOpacity: 0.8
				});
			}
		}).addTo(map);			
			

var mylabels = L.geoJson(punkt, {
	onEachFeature: function (feature, layer) {
		layer.bindPopup('<b>' + feature.properties.name + '</b><br>' +  feature.properties.description);
	}, 
    pointToLayer: function(feature, ll) {
        return L.marker(ll, {
            icon: L.divIcon({
                className: 'mylabel',
                html: feature.properties.name
            })
        });
    }
}).addTo(map);

/* 
var layerControl = L.control.layers(null, { 
			"Oppmøtested" : viktigePunkt, 
			"Henteområde" : henteomr, 
			"Marsjruter":  marsjering, 
			"Navn oppmøtesteder": mylabels,
			"SSM fane": realtime, 
			"Spor etter SSM fane": realtimeLinje
			},  {position: 'bottomright'} ); 
 */

 

var layerControl = L.control.layers(null, { 
			"Marsjruter":  marsjering, 
			"SSM fane": realtime, 
			"Spor etter SSM fane": realtimeLinje
			},  {position: 'bottomright'} ); 
map.addControl(layerControl); 


var firstTime = true; 

realtime.on('update', function(e) {
	
        popupContent = function(fId) {
            var feature = e.features[fId]; 
			var timestamp = new Date( Date.parse( feature.properties.time)); 
			var timePretty = mindato( timestamp ); 
			document.querySelector('#vegreferanse').innerHTML = "SSM fane " + timePretty['klokke'];
            return '<img src="http://labs.ltglahn.no/kart/gps/img/ssmlogo36x55.jpg"><br>' + 
			feature.properties.id + ' var her<br>' + 
					'<b>' + timePretty['klokke'] + "</b><br>" + timePretty['dato'];
        },
        bindFeaturePopup = function(fId) {
            realtime.getLayer(fId).bindPopup(popupContent(fId)).openPopup();
        },
        updateFeaturePopup = function(fId) {
            realtime.getLayer(fId).getPopup().setContent(popupContent(fId));
        };

    Object.keys(e.enter).forEach(bindFeaturePopup);
    Object.keys(e.update).forEach(updateFeaturePopup);

	if (firstTime) {
		map.fitBounds(realtime.getBounds(), {maxZoom: 14});
	}
	
firstTime = false; 
	
	
});
