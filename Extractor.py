import csv
import requests
import re
import os
import time
import pickle
import pandas as pd

LOG = 'D:/Thesis_data/log.txt'
def parse_identity(file1):
    hand=open(file1, encoding='utf-8', errors="replace")
    IDENTITY={}
    for line in hand:
        line=line.strip()
        if re.findall('^COMPANY CONFORMED NAME:',line):
            k = line.find(':')
            comnam=line[k+1:]
            comnam=comnam.strip()
            IDENTITY['name']=str(comnam)                                       
            break
        
    hand.seek(0)
    for line in hand:
        line=line.strip()
        if re.findall('^CENTRAL INDEX KEY:',line):
            k = line.find(':')
            cik=line[k+1:]
            cik=cik.strip()
            IDENTITY['cik']=str(cik)
            break
        
    hand.seek(0)
    for line in hand:
        line=line.strip()
        if re.findall('^STANDARD INDUSTRIAL CLASSIFICATION:',line):
            k = line.find(':')
            sic=line[k+1:]
            sic=sic.strip()
            siccode=[]
            for s in sic: 
                if s.isdigit():
                    siccode.append(s)    
            IDENTITY['sic']=''.join(siccode)
            break
        
    hand.seek(0)
    for line in hand:
        line=line.strip()
        if re.findall('^CONFORMED SUBMISSION TYPE:',line):
            k = line.find(':')
            subtype=line[k+1:]
            subtype=subtype.strip()
            IDENTITY['subtype']=str(subtype)
            break
            
    hand.seek(0)
    for line in hand:
        line=line.strip()
        if re.findall('^CONFORMED PERIOD OF REPORT:',line):
            k = line.find(':')
            cper=line[k+1:]
            cper=cper.strip()
            IDENTITY['CONFORMED DATE']=str(cper)
            break
            
    hand.seek(0)
    for line in hand:
        line=line.strip()
        if re.findall('^FILED AS OF DATE:',line):
            k = line.find(':')
            fdate=line[k+1:]
            fdate=fdate.strip()
            #print fdate                                
            IDENTITY['FILE DATE']=str(fdate)
            break
    
    hand.seek(0)
    for line in hand:
        line=line.strip()
        if re.findall('^FISCAL YEAR END:',line):
            line=line.strip()
            yearend=line[-4:]
            IDENTITY['yearend']= str(yearend)
            break        
    
    hand.close()
    return IDENTITY

def headerclean(content):
    mark0=0
    strings1=['</SEC-HEADER>','</IMS-HEADER>']
    for x, line in enumerate(content.split('\n')):
        line=line.strip()
        if any(s in line for s in strings1):
            mark0=x
            break
    return '\n'.join(content.split('\n')[mark0:])
    
def xbrl_clean(cond1, cond2, str0):
    locations=[0]
    #print locations
    placement1=[]
    str0=str0.lower()
    for m in re.finditer(cond1, str0):
        a=m.start()
        placement1.append(a)
    #print placement1
    
    if placement1!=[]:
        placement2=[]
        for m in re.finditer(cond2, str0):
            a=m.end()
            placement2.append(a)
    #    print placement2
        
        len1=len(placement1)
        placement1.append(len(str0))
        
        for i in range(len1):
            placement3=[]
            locations.append(placement1[i])
            for j in placement2:
                if (j>placement1[i] and j<placement1[i+1]):
                    placement3.append(j)
                    break
            if placement3!=[]:
                locations.append(placement3[0])
            else:
                locations.append(placement1[i])
    
    #print locations
    return locations

def asciireplace(con1, con2, content):
        output=content
        locations_xbrlbig=xbrl_clean(con1, con2, output)
        locations_xbrlbig.append(len(output))
        if locations_xbrlbig!=[0]:
            content=""
            if len(locations_xbrlbig)%2==0:
                for i in range(0,len(locations_xbrlbig),2):
                    content=content+output[locations_xbrlbig[i]:locations_xbrlbig[i+1]]
        return content    

def asciiclean(content):
    
    content = asciireplace("<type>zip", "</document>", content)
    content = asciireplace("<type>graphic", "</document>", content)
    content = asciireplace("<type>excel", "</document>", content)
    content = asciireplace("<type>pdf", "</document>", content)
    content = asciireplace("<type>xml", "</document>", content)
    content = asciireplace("<type>ex", "</document>", content)  
    return content

def tagsclean(content):
    p = re.compile(r'(<DIV.*?>)|(<DIV\n.*?>)|(<DIV\n\r.*?>)|(<DIV\r\n.*?>)|(<DIV.*?\n.*?>)|(<DIV.*?\n\r.*?>)|(<DIV.*?\r\n.*?>)')
    content=p.sub("",content)
    p = re.compile(r'(<div.*?>)|(<div\n.*?>)|(<div\n\r.*?>)|(<div\r\n.*?>)|(<div.*?\n.*?>)|(<div.*?\n\r.*?>)|(<div.*?\r\n.*?>)')
    content=p.sub("",content)
    p = re.compile(r'(<TD.*?>)|(<TD\n.*?>)|(<TD\n\r.*?>)|(<TD\r\n.*?>)|(<TD.*?\n.*?>)|(<TD.*?\n\r.*?>)|(<TD.*?\r\n.*?>)')
    content=p.sub("",content)
    p = re.compile(r'(<td.*?>)|(<td\n.*?>)|(<td\n\r.*?>)|(<td\r\n.*?>)|(<td.*?\n.*?>)|(<td.*?\n\r.*?>)|(<td.*?\r\n.*?>)')
    content=p.sub("",content)
    p = re.compile(r'(<TR.*?>)|(<TR\n.*?>)|(<TR\n\r.*?>)|(<TR\r\n.*?>)|(<TR.*?\n.*?>)|(<TR.*?\n\r.*?>)|(<TR.*?\r\n.*?>)')
    content=p.sub("",content)
    p = re.compile(r'(<tr.*?>)|(<tr\n.*?>)|(<tr\n\r.*?>)|(<tr\r\n.*?>)|(<tr.*?\n.*?>)|(<tr.*?\n\r.*?>)|(<tr.*?\r\n.*?>)')
    content=p.sub("",content)
    p = re.compile(r'(<FONT.*?>)|(<FONT\n.*?>)|(<FONT\n\r.*?>)|(<FONT\r\n.*?>)|(<FONT.*?\n.*?>)|(<FONT.*?\n\r.*?>)|(<FONT.*?\r\n.*?>)')
    content=p.sub("",content)
    p = re.compile(r'(<font.*?>)|(<font\n.*?>)|(<font\n\r.*?>)|(<font\r\n.*?>)|(<font.*?\n.*?>)|(<font.*?\n\r.*?>)|(<font.*?\r\n.*?>)')
    content=p.sub("",content)
    p = re.compile(r'(<P.*?>)|(<P\n.*?>)|(<P\n\r.*?>)|(<P\r\n.*?>)|(<P.*?\n.*?>)|(<P.*?\n\r.*?>)|(<P.*?\r\n.*?>)')
    content=p.sub("",content)
    p = re.compile(r'(<p.*?>)|(<p\n.*?>)|(<p\n\r.*?>)|(<p\r\n.*?>)|(<p.*?\n.*?>)|(<p.*?\n\r.*?>)|(<p.*?\r\n.*?>)')
    content=p.sub("",content)
    content=content.replace("</DIV>","")
    content=content.replace("</div>","")
    content=content.replace("</TR>","")
    content=content.replace("</tr>","")
    content=content.replace("</TD>","")
    content=content.replace("</td>","")
    content=content.replace("</FONT>","")
    content=content.replace("</font>","")
    content=content.replace("</P>","")
    content=content.replace("</p>","")
    return content

def table_clean(cond1, cond2, str1):
    Items0=["item 7", "item7", "item8", "item 8"]
    Items1=["item 1", "item 2","item 3","item 4","item 5","item 6","item 9", "item 10", "item1", "item2","item3","item4","item5","item6","item9", "item10"]
    
    str2=str1.lower()
    placement1=[]
    for m in re.finditer(cond1, str2):
        a=m.start()
        placement1.append(a)
    n=len(placement1)
    placement1.append(len(str2))
    
    placement2=[]
    for m in re.finditer(cond2, str2):
        a=m.end()
        placement2.append(a)
        
    if (placement1!=[] and placement2!=[]):
        current=str1[0:placement1[0]]
        
        for i in range(n):
            begin=placement1[i]
            for j in placement2:
                if j>begin:
                    end=j
                    break
            
            if end=="":
                current=current+str1[begin:placement1[i+1]]
            else:
                str2=""
                str2=str1[begin:end].lower()
                str2=str2.replace("&nbsp;"," ")
                str2=str2.replace("&NBSP;"," ")
                p = re.compile(r'&#\d{1,5};')
                str2=p.sub("",str2)
                p = re.compile(r'&#.{1,5};')
                str2=p.sub("",str2)
                if any(s in str2 for s in Items0):
                    if not any(s in str2 for s in Items1):
                        current=current+str2
                    
                current=current+str1[end:placement1[i+1]]
                end=""
    else:
        current=str1
    return current

def cleannewline(content):
    content=content.replace("\r\n"," ")
    p = re.compile(r'<.*?>')
    content=p.sub("",content)
    return content

def cleanothers(content):
    content=content.replace("&nbsp;"," ")
    content=content.replace("&NBSP;"," ")
    content=content.replace("&LT;","LT")
    content=content.replace("&#60;","LT")
    content=content.replace("&#160;"," ")
    content=content.replace("&AMP;","&")
    content=content.replace("&amp;","&")
    content=content.replace("&#38;","&")
    content=content.replace("&APOS;","'")
    content=content.replace("&apos;","'")
    content=content.replace("&#39;","'")
    content=content.replace('&QUOT;','"')
    content=content.replace('&quot;','"')
    content=content.replace('&#34;','"')
    content=content.replace("\t"," ")
    content=content.replace("\v","")
    content=content.replace("&#149;"," ")
    content=content.replace("&#224;","")
    content=content.replace("&#145;","")
    content=content.replace("&#146;","")
    content=content.replace("&#147;","")
    content=content.replace("&#148;","")
    content=content.replace("&#151;"," ")
    content=content.replace("&#153;","") 
    content=content.replace("&#111;","")
    content=content.replace("&#153;","")
    content=content.replace("&#253;","")
    content=content.replace("&#8217;","")
    content=content.replace("&#32;"," ")
    content=content.replace("&#174;","")
    content=content.replace("&#167;","")
    content=content.replace("&#169;","")
    content=content.replace("&#8220;","")
    content=content.replace("&#8221;","")
    content=content.replace("&rsquo;","")
    content=content.replace("&lsquo;","")
    content=content.replace("&sbquo;","")
    content=content.replace("&bdquo;","")
    content=content.replace("&ldquo;","")
    content=content.replace("&rdquo;","")
    content=content.replace("\'","")
    p = re.compile(r'&#\d{1,5};')
    content=p.sub("",content)
    p = re.compile(r'&#.{1,5};')
    content=p.sub("",content)
    content=content.replace("_"," ")
    content=content.replace("and/or","and or")
    content=content.replace("-\n"," ")
    p = re.compile(r'\s*-\s*')
    content=p.sub(" ",content)
    p = re.compile(r'(-|=)\s*')
    content=p.sub(" ",content)
    p = re.compile(r'\s\s*')
    content=p.sub(" ",content)
    p = re.compile(r'(\n\s*){3,}')
    content=p.sub("\n\n",content)
    p = re.compile(r'<.*?>')
    content=p.sub("",content)
    content = content.replace("'", "")
    return content

def cleancontent(content):
    content = headerclean(content)
    content = asciiclean(content)
    # content = tagsclean(content)# 很久，可能要改
    content = asciireplace("<xbrl", "</xbrl.*>", content)
    # content = table_clean('<table','</table>',content)
    content = cleannewline(content)
    content = cleanothers(content)
    return content

def findmda(content, path):
    item7={}
    item7[1]="item 7. managements discussion and analysis"
    item7[2]="item 7.managements discussion and analysis"
    item7[3]="item7. managements discussion and analysis"
    item7[4]="item7.managements discussion and analysis"
    item7[5]="item 7. management discussion and analysis"
    item7[6]="item 7.management discussion and analysis"
    item7[7]="item7. management discussion and analysis"
    item7[8]="item7.management discussion and analysis"
    item7[9]="item 7 managements discussion and analysis"
    item7[10]="item 7managements discussion and analysis"
    item7[11]="item7 managements discussion and analysis"
    item7[12]="item7managements discussion and analysis"
    item7[13]="item 7 management discussion and analysis"
    item7[14]="item 7management discussion and analysis"
    item7[15]="item7 management discussion and analysis"
    item7[16]="item7management discussion and analysis"
    item7[17]="item 7: managements discussion and analysis"
    item7[18]="item 7:managements discussion and analysis"
    item7[19]="item7: managements discussion and analysis"
    item7[20]="item7:managements discussion and analysis"
    item7[21]="item 7: management discussion and analysis"
    item7[22]="item 7:management discussion and analysis"
    item7[23]="item7: management discussion and analysis"
    item7[24]="item7:management discussion and analysis"
    item8={}
    item8[1]="item 8. financial statements"
    item8[2]="item 8.financial statements"
    item8[3]="item8. financial statements"
    item8[4]="item8.financial statements"
    item8[5]="item 8 financial statements"
    item8[6]="item 8financial statements"
    item8[7]="item8 financial statements"
    item8[8]="item8financial statements"
    item8[9]="item 8a. financial statements"
    item8[10]="item 8a.financial statements"
    item8[11]="item8a. financial statements"
    item8[12]="item8a.financial statements"
    item8[13]="item 8a financial statements"
    item8[14]="item 8afinancial statements"
    item8[15]="item8a financial statements"
    item8[16]="item8afinancial statements"
    item8[17]="item 8. consolidated financial statements"
    item8[18]="item 8.consolidated financial statements"
    item8[19]="item8. consolidated financial statements"
    item8[20]="item8.consolidated financial statements"
    item8[21]="item 8 consolidated  financial statements"
    item8[22]="item 8consolidated financial statements"
    item8[23]="item8 consolidated  financial statements"
    item8[24]="item8consolidated financial statements"
    item8[25]="item 8a. consolidated financial statements"
    item8[26]="item 8a.consolidated financial statements"
    item8[27]="item8a. consolidated financial statements"
    item8[28]="item8a.consolidated financial statements"
    item8[29]="item 8a consolidated financial statements"
    item8[30]="item 8aconsolidated financial statements"
    item8[31]="item8a consolidated financial statements"
    item8[32]="item8aconsolidated financial statements"
    item8[33]="item 8. audited financial statements"
    item8[34]="item 8.audited financial statements"
    item8[35]="item8. audited financial statements"
    item8[36]="item8.audited financial statements"
    item8[37]="item 8 audited financial statements"
    item8[38]="item 8audited financial statements"
    item8[39]="item8 audited financial statements"
    item8[40]="item8audited financial statements"
    item8[41]="item 8: financial statements"
    item8[42]="item 8:financial statements"
    item8[43]="item8: financial statements"
    item8[44]="item8:financial statements"
    item8[45]="item 8: consolidated financial statements"
    item8[46]="item 8:consolidated financial statements"
    item8[47]="item8: consolidated financial statements"
    item8[48]="item8:consolidated financial statements"
    
    look={" see ", " refer to ", " included in "," contained in "}
    a={}
    c={}
    
    lstr1=content.lower()
    for j in range(1,25):
        a[j]=[]
        for m in re.finditer(item7[j], lstr1):
            if not m:
                break
            else:
                substr1=lstr1[m.start()-20:m.start()]
                if not any(s in substr1 for s in look):   
                    #print substr1
                    b=m.start()
                    a[j].append(b)
    #print i
    
    list1=[]
    for value in a.values():
        for thing1 in value:
            list1.append(thing1)
    list1.sort()
    list1.append(len(lstr1))
    #print list1
           
    for j in range(1,49):
        c[j]=[]
        for m in re.finditer(item8[j], lstr1):
            if not m:
                break
            else:
                substr1=lstr1[m.start()-20:m.start()]
                if not any(s in substr1 for s in look):   
                    #print substr1
                    b=m.start()
                    c[j].append(b)
    list2=[]
    for value in c.values():
        for thing2 in value:
            list2.append(thing2)
    list2.sort()
    
    locations={}
    if list2==[]:
        print(path + " NO MD&A")
    else:
        if list1==[]:
            print(path + " NO MD&A")
        else:
            for k0 in range(len(list1)):
                locations[k0]=[]
                locations[k0].append(list1[k0])
            for k0 in range(len(locations)):
                for item in range(len(list2)):
                    if locations[k0][0]<=list2[item]:
                        locations[k0].append(list2[item])
                        break
                if len(locations[k0])==1:
                    del locations[k0]
    output = ''
    if locations=={}:
        with open(LOG,'a') as f:
            f.write(str(path)+"\t"+"0"+"\t"+"0\n")
            f.close()
    else:
        sections=0
        short = 0
        for k0 in range(len(locations)): 
            substring2=content[locations[k0][0]:locations[k0][1]]
            n_words=substring2.split()
            if len(n_words)>50:
                sections=sections+1
                output = output + substring2 + "\n"
            else:
                short = short+1
        with open(LOG,'a') as f:
                f.write(str(path)+"\t"+str(sections)+"\t"+str(short)+"\n")
                f.close()
    return output

def extract_item(path):
    identity = parse_identity(path)
    with open(path, 'r', encoding='utf-8', errors="replace") as f:
        content = f.read() 
    content = cleancontent(content)
    identity['mda'] = findmda(content, path)
    return identity