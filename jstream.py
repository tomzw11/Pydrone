import execjs

ctx = execjs.compile('''
var bebop = require("/Users/Tom/Desktop/node_modules/node-bebop/lib");

var drone = bebop.createClient();

function conn(){
  return drone.connect(function() {
    
    drone.MediaStreaming.videoStreamMode(2);
    drone.MediaStreaming.videoEnable(1);

  });
}
''')

# drone.MediaStreaming.videoStreamMode(2);
#     drone.PictureSettings.videoStabilizationMode(3);

print(ctx.call('conn'))