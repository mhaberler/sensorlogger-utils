BASECOORDS = [47.07585724136853, 15.431147228565663];

function makeMap() {
    mymap = L.map('llmap').setView(BASECOORDS, 8);
    var layer = protomaps.leafletLayer({ url: 'https://static.mah.priv.at/cors/pmtiles/europe-latest.pmtiles' })
    layer.addTo(mymap)
    layer.addInspector(mymap)
}

var layer = L.layerGroup();

function renderData(districtid) {
    $.getJSON("/district/" + districtid, function (obj) {
        var markers = obj.data.map(function (arr) {
            return L.marker([arr[0], arr[1]]);
        });
        mymap.removeLayer(layer);
        layer = L.layerGroup(markers);
        mymap.addLayer(layer);
    });
}


$(function () {
    makeMap();
    renderData('0');
    $('#distsel').change(function () {
        var val = $('#distsel option:selected').val();
        renderData(val);
    });
})
