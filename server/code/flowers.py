from preconfig import PreConfig
import json
class Flowers:
    def __init__(self,pc = None):
        if pc:
            self.pc = pc
        else:
            self.pc = PreConfig()
            self.rc = self.pc.rc

    def get(self):
        return self.gather(self.pc.config['redis']['liveflowers'])

    def id(self,fid):
        try:
            lfid = self.pc.config['redis']['liveflowers'] + fid
            flower = json.loads(self.rc.get(lfid).decode('utf-8'))
            return flower
        except Exception as e:
            print(e)
            return {}

    def getDead(self):
        return self.gather(self.pc.config['redis']['deadflowers'])

    # pulls all flowers based on the prefix.
    #  helper function for getting live and dead flowers
    def gather(self,prefix):
        try:
            flowers = {}
            afids = self.rc.keys(prefix + '*')
            for afid in afids:
                flower = json.loads(self.rc.get(afid).decode('utf-8'))
                fid = afid.decode('utf-8').split(':',1)[1]
                flowers[fid] = flower
            return flowers
        except Exception as e:
            print(e)
            return {}