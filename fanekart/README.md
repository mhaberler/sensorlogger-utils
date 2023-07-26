# fanekart
A web application for live tracking of your smart phone GPS, or any device capable of sending coordinates to a web server on the form: 
```
https://yourserver.com/gpsId/secretKey?lon=61.5555&lat=7.4444 
```
Personally, I've used [self hosted GPS tracker](https://play.google.com/store/apps/details?id=fr.herverenault.selfhostedgpstracker) at an old Android phone. Simular apps are available for Iphone, but I haven't tested any. 

For server backend, I've choosen [pythonanywhere](https://www.pythonanywhere.com), a cloud hosting provider for with a strong love for web applications written in python *(and a great starting point for anyone who wants to learn python, but can't or won't install anything at their local machine)*. Their free account is plenty for this application (but you won't regret shilling out for their paid services, starting at $5/mo). 

Getting this up and running at your own flask web server should also be easy. Just look at the installation script to see where to change links, folder names. 

Live tracking is shown on a simple Leaflet (javascript) map. For convenience, this is hosted together with the backend server, but it can be hosted on any web server. 

## [Installation](https://github.com/LtGlahn/fanekart/blob/master/install.md). 