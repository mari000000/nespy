import os


'''
Reference @ https://wiki.nesdev.com/w/index.php/NES_2.0
'''
class nesCart:
    mapperList = {
        0  : 'No Mapper',                                 
        1  : 'Nintendo MMC1 Chipset',  
        2  : 'ROM (PRG) Switch',  
        3  : 'VROM (CHR) Switch',  
        4  : 'Nintendo MMC3 Chipset',  
        5  : 'Nintendo MMC5 Chipset',  
        6  : 'FFE F4XXX Games',  
        7  : '32kb ROM (PRG) Switch',  
        8  : 'FFE F3XXX Games',  
        9  : 'Nintendo MMC2 Chipset',  
        10 : 'Nintendo MMC4 Chipset',  
        11 : 'Color Dreams Chipset',  
        12 : 'FFE F6XXX Games',  
        15 : '100-in-1 Cart Switch',  
        16 : 'Ban Dai Chipset',
        17 : 'FFE F8XXX Games',
        18 : 'Jaleco SS8806 Chipset',
        19 : 'Namcot 106 Chipset',
        20 : 'Famicom Disk System',
        21 : 'Konami VRC4 2a Chipset',
        22 : 'Konami VRC4 1b Chipset',
        23 : 'Konami VRC4 1a Chipset',
        24 : 'Konami VRC6 Chipset',
        25 : 'Konami VRC4 Chipset',
        32 : 'Irem G-101 Chipset',
        33 : 'Taito TC0190/TC0350',
        34 : '32kb ROM (PRG) Switch',
        65 : 'Irem H3001 Chipset',
        66 : '74161/32 Chipset',
        67 : 'Sunsoft Mapper 3',
        69 : 'Sunsoft Mapper 4',
        70 : '74161/32 Chipset',
        80 : 'X-005 Chipset',
        81 : 'C075 Chipset',
        82 : 'X1-17 Chipset',
        83 : 'Cony Mapper',
        84 : 'PasoFami Mapper!',
    }

    displayList = {
        0x00 : 'H (Horizontal Mirroring ONLY)',
        0x01 : 'V (Vertical Mirroring ONLY)',
        0x02 : 'H + Bat. (Horizontal Mirroring + Battery ON)',
        0x03 : 'V + Bat. (Vertical Mirroring + Battery ON)',
        0x04 : 'H + Train. (Horizontal Mirroring + Trainer ON)',
        0x05 : 'V + Train. (Vertical Mirroring + Trainer ON)',
        0x06 : 'H + Bat. + Train. (Horizontal Mirroring + Battery and Trainer ON)',
        0x07 : 'V + Bat. + Train. (Vertical Mirroring + Battery and Trainer ON)',
        0x08 : 'H + 4scr. (Horizontal Mirroring + 4 Screen VRAM ON)',
        0x09 : 'V + 4scr. (Vertical Mirroring + 4 Screen VRAM ON)',
        0x0A : 'H + Bat. + 4scr. (Horizontal Mirroring + Battery and 4 Screen VRAM ON)',
        0x0B : 'V + Bat. + 4scr. (Vertical Mirroring + Battery and 4 Screen VRAM ON)',
        0x0C : 'H + 4scr. + Train. (Horizontal Mirroring + 4 Screen VRAM and Trainer ON)',
        0x0D : 'V + 4scr. + Train. (Vertical Mirroring + 4 Screen VRAM and Trainer ON)',
        0x0E : 'H + Bat. + 4scr. + Train. (Horizontal Mirroring + Battery, 4 Screen VRAM, and Trainer ON)',
        0x0F : 'V + Bat. + 4scr. + Train. (Vertical Mirroring + Battery, 4 Screen VRAM, and Trainer ON)',
    }

    def __init__(self, filePath=None):
        try:
            with open(filePath, 'rb') as cart:
                nesHeader = cart.read(16)
                if '/' in filePath:
                    self.game = filePath.split('/')[-1]
                else:
                    self.game = filePath
                if nesHeader[:3] != b'NES':
                    print("Invalid File Type, Did you try Blowing On It?")
                    return None
                
                self.prgmSize = nesHeader[4]
                self.chrSize = nesHeader[5]
                self.mapper = ((nesHeader[6] & 0xF0) >> 4) | (nesHeader[7] & 0xF0)
                
                # Flags 6
                self.flags6 = nesHeader[6] & 0x0F
                # 0 = horizontal or mapper mirrorint; 1 = vertical mirroring
                self.mirroring = 1 if nesHeader[6] & 0x01 == 0x01 else 0

                # 0 = Battery not preset; 1 = battery present
                self.battery = 1 if nesHeader[6] & 0x02 == 0x02 else 0

                # 1 = 512 Byte trainer present 
                self.trainer = 1 if nesHeader[6] & 0x04 == 0x04 else 0

                # 1 = hardwired 4 screen present
                self.fourScreen = 1 if nesHeader[6] & 0x08 == 0x08 else 0
                # for s in nesHeader:
                #     print(s)
                # pass
                if self.trainer:
                    self.trainerROM = cart.read(512)
                
                self.PRGM = []
                for _ in range(self.prgmSize):
                    # store 16k pages
                    self.PRGM.append(cart.read(1024*16))
                
                self.CHR = []
                for _ in range(self.chrSize):
                    # store 8k pages
                    self.CHR.append(cart.read(1024*8))
                
        except:
            print("Failed to open game cartridge, Try Blowing On It!")

    def __str__(self) -> str:
        ret = f"""{self.game}
            PRGSize: {self.prgmSize * 16}k
            CHRSize: {self.chrSize * 8}k
            Mapper: {self.mapperList[self.mapper]}
            Flags: {self.displayList[self.flags6]}\n"""
        return ret


def main():
    gameHeaderInfo = []

    for game in os.listdir('../nes'):
        if game.endswith('.nes'):
            gameHeaderInfo.append(nesCart(f'../nes/{game}'))

    for game in gameHeaderInfo:
        print(game)

if __name__ == "__main__":
    main()