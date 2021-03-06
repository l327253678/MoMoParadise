from Module import ldconsole
#import ldconsole
import time
import os
from PIL import Image
import imagehash
import cv2 as cv
import numpy as np
# If global var stop_cap is needed
#import globals
from threading import Thread



class LM(object):
    def __init__(self,Index_Num: int,Sample_Path):
       #self.ADB = adb.ADB(Device_Name=Device_Name,Screen_Size=[1280,720])
       self.DnPlayer = ldconsole.DnPlayer(ldconsole.Dnconsole.get_list_info(Index_Num))
       self.Index_Num = Index_Num
       self.Sample_Image = dict()
       self.Import_Sample_Image(Sample_Path)
       self.Screen_Now = None
       self.Stop_Cap = False
       self.Safe_Area = None
       self.PVP_status = False

    
    def Import_Sample_Image(self,Path):
        if os.path.isdir(Path) == False:
            print("Sample Dir not exits")
            return 0
        File_List = os.listdir(Path)

        for File_Name in File_List:
            File_Index = File_Name.replace(".jpg","")
            self.Sample_Image[File_Index] = Path+"/"+ File_Name

        print("Images imported")

    def Get_Emu_Img_now(self):
        while 1:
            try:
                BGR_img = cv.cvtColor(ldconsole.Dnconsole.getWindow_Img_new(self.Index_Num), cv.COLOR_BGRA2BGR)
                self.Screen_Now = BGR_img
                time.sleep(1)
            except: ###keyboard interrupt removed
                pass
            if self.Stop_Cap:
                break

    def Keep_Emu_Img_Cap(self):
        th = Thread(target=self.Get_Emu_Img_now,args= [],daemon=True)
        th.start()
    

    @staticmethod
    def Check_Safe_Area_fn(src_img, temp_img, threshold):
        res = LM.Image_CMP_fn(im_src, temp_img, threshold)
        if res != 0:
            print('Safe Area')
        else:
            print('Wild Area')
    
    def Check_Safe_Area(self):
        res = self.Image_CMP_new(temp_img = 'safe_area.jpg', threshold = 0.7)
        if res != 0:
            self.Safe_Area = True
        else:
            self.Safe_Area = False
        

    @staticmethod
    def Image_CMP_fn(src_img, temp_img, threshold):
        img_src = cv.imread(src_img)
        #cv.imwrite('src1.jpg',img_src)
        #im1 = cv.cvtColor(img_src, cv.COLOR_BGRA2BGR)
        #cv.imwrite('src2.jpg',img_src)
        template = cv.imread(temp_img)
        #print(template.shape)
        
        res = cv.matchTemplate(img_src, template, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        #cv.imwrite('img_cmp.jpg',img_src)
        #cv.imwrite('temp.jpg',template)
        print(max_val)
        
        if max_val > threshold:
            return max_loc
        else:
            print('Not found')
            return 0

    def Image_CMP_new(self,temp_img,threshold):
        im1 = self.Screen_Now
        #print(im1)
        #cv.imwrite('src1.jpg',img_src)
        #im1 = cv.cvtColor(img_src, cv.COLOR_BGRA2BGR)
        #cv.imwrite('src2.jpg',img_src)
        template = cv.imread(temp_img)
        #print(template.shape)
        
        res = cv.matchTemplate(im1, template, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        #cv.imwrite('img_cmp.jpg',img_src)
        #cv.imwrite('temp.jpg',template)
        print(max_val)
        
        if max_val > threshold:
            return max_loc
        else:
            print('Not found')
            return 0
    
    @staticmethod
    def Detect_Menu_Red_Point_fn(src_img: str):
        target_img = cv.imread(src_img)[0:363,889:1262]
        #im_HSV = cv.cvtColor(target_img, cv.COLOR_BGR2HSV)
        
        b_channel=0
        g_channel=1
        r_channel=2

        r_query = 255
        loc = np.where((target_img[:,:,r_channel] == r_query))

        y_loc = loc[0]
        x_loc = loc[1]
        
        dungeon_point = [51,164]
        sign_in_point = [203,164]
        mail_point = [203,306]
        menu_point = [356,25]
        
        #print(loc)
        print(sign_in_point[0] in x_loc)
        print(sign_in_point[1] in y_loc)
     
    @staticmethod
    def Detect_HP_Above_80_fn(src_img: str):
        # Lineage M HP : Top-Left = [74,17], Bot-Right = [264,29]
        # length = 190, width = 12
        # 90% = 74 + 190 * 0.9 => [245,23]
        # 80% => [226, 23]
        # 70% => [207, 23]
        # 60% => [188, 23]
        # 50% => [169, 23]
        # 40% => [150, 23]

        #print(src_img)
        target_img = cv.imread(src_img)[17:29, 74:264]
        im_HSV = cv.cvtColor(target_img, cv.COLOR_BGR2HSV)
        
        # Red Mask
        lower_red = np.array([0,43,150]) 
        upper_red = np.array([10,255,255])
        red_mask = cv.inRange(im_HSV, lower_red, upper_red)
        # test if HP is correctly filtered
        #res_img = cv.imwrite('res.jpg',red_mask)

        
        # Green Mask
        lower_green = np.array([50,43,46]) 
        upper_green = np.array([70,255,255])
        green_mask = cv.inRange(im_HSV, lower_green, upper_green)

        if green_mask[6,38] == 255:
            return 1 # green, poisoned
        elif red_mask[6,152] == 255:
            return 2 # HP above 80%
        else:
            return 0 # gray

    def Detect_HP_Above_80(self):
        # Lineage M HP : Top-Left = [74,17], Bot-Right = [264,29]
        # length = 190, width = 12
        # 90% = 74 + 190 * 0.9 => [245,23]
        # 80% => [226, 23]
        # 70% => [207, 23]
        # 60% => [188, 23]
        # 50% => [169, 23]
        # 40% => [150, 23]

        #print(src_img)
        target_img = self.Screen_Now[17:29, 74:264]
        im_HSV = cv.cvtColor(target_img, cv.COLOR_BGR2HSV)
        
        # Red Mask
        lower_red = np.array([0,43,150]) 
        upper_red = np.array([10,255,255])
        red_mask = cv.inRange(im_HSV, lower_red, upper_red)
        # test if HP is correctly filtered
        #res_img = cv.imwrite('res.jpg',red_mask)

        
        # Green Mask
        lower_green = np.array([50,43,46]) 
        upper_green = np.array([70,255,255])
        green_mask = cv.inRange(im_HSV, lower_green, upper_green)

        if green_mask[6,38] == 255:
            return 1 # green, poisoned
        elif red_mask[6,152] == 255:
            #print('HP High 123')
            return 2 # HP above 80%
        else:
            #print('HP low 123')
            return 0 # gray

    @staticmethod
    def Detect_PVP_fn(src_img: str):
        target_img = cv.imread(src_img)[515:574, 1162:1221]
        im_HSV = cv.cvtColor(target_img, cv.COLOR_BGR2HSV)
        # Red Mask
        lower_red = np.array([0,43,150]) 
        upper_red = np.array([10,255,255])
        red_mask = cv.inRange(im_HSV, lower_red, upper_red)
        # test if HP is correctly filtered
        # res_img = cv.imwrite('res.jpg',red_mask)
        if red_mask[25,25] and red_mask[25,36] and red_mask[35,31]:
            print("PVP engaged")
            return True
        else:
            return False
    
    def Detect_PVP(self):
        target_img = self.Screen_Now[515:574, 1162:1221]
        im_HSV = cv.cvtColor(target_img, cv.COLOR_BGR2HSV)
        # Red Mask
        lower_red = np.array([0,43,150]) 
        upper_red = np.array([10,255,255])
        red_mask = cv.inRange(im_HSV, lower_red, upper_red)
        # test if HP is correctly filtered
        # res_img = cv.imwrite('res.jpg',red_mask)
        if red_mask[25,25] and red_mask[25,36] and red_mask[35,31]:
            print("PVP engaged")
            self.PVP_status = True
        else:
            print('Not PVP')
            self.PVP_status = False
    
    @staticmethod
    def Check_Monster_fn(src_img: str):
        tg = LM.Image_CMP_fn(src_img, temp_img = 'evil_liz_tg.jpg', threshold = 0.9)
        if tg != 0:
            print('Detected')

    def Check_Monster(self,temp_img: str):
        tg = self.Image_CMP_new(temp_img, threshold = 0.9)
        if tg != 0:
            print('Detected')

    
    
    @staticmethod
    def Check_Orange_Potion_fn(src_img: str):
        org_mil_loc = ldconsole.Dnconsole.find_pic(screen = src_img, template = 'orange_potion_low.jpg', threshold = 0.008)
        print(org_mil_loc)

    def Check_Orange_Potion_low(self):
        org_loc = self.Image_CMP_new(temp_img = 'orange_potion_low.jpg', threshold = 0.99)
        print(org_loc)
        if org_loc == 0:
            print('Good')
            return 0
        elif org_loc[0] in range(921,987):
            print('Low')
            return 1
        else:
            print('Retry')
    
    @staticmethod
    def Check_Orange_Potion_zero(src_img: str):
        org_mil_loc = ldconsole.Dnconsole.find_pic(screen = src_img, template = 'orange_potion_zero.jpg', threshold = 0.008)
        print(org_mil_loc)
        
    
    def Check_Red_Potion_low(self):
        red_loc = self.Image_CMP_new(temp_img = 'red_water_10.jpg', threshold = 0.99)
        print(red_loc)
        if red_loc == 0:
            print('Good')
            return 0
        elif red_loc[0] in range(921,987):
            print('Low')
            return 1
        else:
            print('Retry')

    def Click_System_Btn(self,name):
        Btn_Map = {}
        Btn_Map['F1'] = [544, 637]
        Btn_Map['F2'] = [620, 637]
        Btn_Map['F3'] = [706, 637]
        Btn_Map['F4'] = [784, 637]
        Btn_Map['Special_Item'] = [860, 637]
        Btn_Map['F5'] = [960, 637]
        Btn_Map['F6'] = [1047, 637]
        Btn_Map['F7'] = [1125, 637]
        Btn_Map['F8'] = [1203, 637]
        Btn_Map['Auto'] = [970, 512]
        Btn_Map['Self'] = [1060, 402]
        Btn_Map['Pick_up'] = [1168, 429]
        Btn_Map['Attack'] = [1104, 520]
        Btn_Map['Store'] = [935, 45]
        Btn_Map['Item_Box'] = [1009, 45]
        Btn_Map['Skill'] = [1080, 45]
        Btn_Map['Mission'] = [1161, 45]
        Btn_Map['Mission_Close_Menu'] = [1237, 45]
        Btn_Map['Menu'] = [1237, 45]
        Btn_Map['Menu_Sign_in'] = [1082, 185]
        Btn_Map['Menu_Mail_Box'] = [1006, 327]
        Btn_Map['Menu_Mail_Box_All_Taken'] = [1084, 662]
        
        if name not in Btn_Map:
            print("無此按鍵名稱：{}".format(name))
            return 0

        click_loc = Btn_Map[name]
        ldconsole.Dnconsole.touch(index = self.Index_Num, x = click_loc[0], y =click_loc[1])
   




if __name__ == '__main__':
    ### Remember ldconsole.Dnconsole.getWindow_Img_new will save images!!!!


    ### Test global var to stop thread
    #globals.initialize()
    #print(globals.stop_cap)
    #obj = LM(1, "./Data/Sample_img")
    #t1 = ldconsole.Dnconsole.Keep_Game_ScreenHot(1)
    #time.sleep(5)
    #globals.stop_cap = True
    #print(globals.stop_cap)
    ### Test global var to stop thread

    ### Test HP Detection
    #print(LM.HPDetect_Above_80('Emu_0_now.jpg'))
    #im1 = ldconsole.Dnconsole.getWindow_Img_new(1)
    ### Test HP Detection

    ### Cap and Crop
    #im1 = cv.imread('evil_liz_normal.jpg')[215:241, 20:119]
    #cv.imwrite('evil_liz_tg.jpg',im1)
    #print(im1.shape)
    ### Cap and Crop
    
    #LM.Check_Monster_fn('evil_liz_normal.jpg')
    #LM.Check_Monster_fn('evil_liz_red.jpg')
    #LM.Check_Monster_fn('emu_2_now.jpg')

    
    #im1 = cv.imread('safe_area.jpg')
    #lower_blue = np.array([100,0,0]) 
    #upper_blue = np.array([140,255,255])
    #blue_mask = cv.inRange(im1, lower_blue, upper_blue)
    #cv.imwrite('filtered_SA.jpg', blue_mask)
    
    ### Check self functions
    #obj = LM(2, "./Data/Sample_img")
    #obj.Keep_Emu_Img_Cap()
    #time.sleep(0.5)
    
    #obj.Check_Monster('evil_liz_tg.jpg')
    
    ### Check self functions

    ### Self Safe Area
    #obj.Check_Safe_Area()
    #print(obj.Safe_Area)

    

    ### Check item: 30 org = 0.00874, 20 org = 0.00793 , 10 org = 0.00109, thus for 10 org potions, threshold could be 0.008
    #LM.Check_Orange_Potion_zero('Emu_1_now.jpg')
    #ldconsole.Dnconsole.getWindow_Img_new(1)
    #print(LM.Check_Orange_Potion('org_potion_10.jpg'))
    #LM.Detect_PVP('PVP.jpg')
    #time.sleep(5)
    #a.Stop_Cap = True
    
    ### Check Emu Running
    obj = LM(2, "./Data/Sample_img")
    obj.Keep_Emu_Img_Cap()

    #time.sleep(0.5)
    #obj.Detect_PVP()

    ### Check Orange potion
    #res = obj.Check_Orange_Potion_low()
    #print(res)
    
    #obj.Click_System_Btn('F4')
    #print(a.Screen_Now)