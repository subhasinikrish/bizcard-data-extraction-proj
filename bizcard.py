import streamlit as st
import easyocr
from PIL import Image
import re
import pandas as pd
import os
import numpy as np
#import sys
#from io import BytesIO,StringIO

import mysql.connector



def show_card(img):
    image=Image.open(img)
    return image

connection=mysql.connector.connect(host="localhost",user="root",password="12345",database="bizcardproject")
mycursor=connection.cursor()

query1="""create table if not exists bizcard_info(Cardholder_name varchar(100) primary key,Designation varchar(50),Phone_number varchar(50),Website_url varchar(50),Email_Id varchar(50),Street_number	varchar(50),
        City varchar(50),State varchar(50),Pincode	int,Company_name varchar(50)
        )"""
mycursor.execute(query1)
connection.commit()

    



def card_reader(img):
   
    
    reader=easyocr.Reader(['en'])

    result=reader.readtext(img,detail=0,paragraph=True)
   
    result1=' '.join(result)
    result1=result1.replace(',','').replace(';','').replace('  ',' ')


    column={"Name":[],"Designation":[],"Phone_number":[],"Website_url":[],"Email_Id":[],"Street_number":[],"City":[],"State":[],"Pincode":[],"Company_name":[]}

    data=result[0].split(' ')
    n=len(data)
    name=data[0]
    designation=''
    for i in range(1,n):
        designation=designation+data[i]+' '

    
    column["Name"].append(name)

    designation=data[1]+data[2]
    column["Designation"].append(designation)

    phone_number=re.findall(r'[\+, ]\d{2,3}-\d{3}-\d{4}',result1)
    column["Phone_number"].append(phone_number[0])

    email=re.findall(r'\w+@\w+.\w+',result1)
    column["Email_Id"].append(email[0])
    
    web=re.findall(r'\w+[WWW,www].\w+.\w+',result1)
    website=' '.join(web).replace(' ','.')
    column["Website_url"].append(website)
    
    street=re.findall(r'\d+ \w+ [St]+',result1)
    column["Street_number"].append(street[0])

    pincode=re.findall(r'\d{6}',result1)
    column["Pincode"].append(pincode[0])

    state=re.findall(r'(\w+) \d{6}',result1)
    column["State"].append(state[0])

    city=re.findall(r'[St]+ (\w+)',result1)
    column["City"].append(city[0])

    
    company_name=result[-1]
    column["Company_name"].append(company_name)


            

    df=pd.DataFrame(column)


    try:
        rows=[]
        for index in df.index:
            row=tuple(df.loc[index].values)
            row=tuple([str(d) for d in row])
            rows.append(row)
        
            

            connection=mysql.connector.connect(host="localhost",user="root",password="12345",database="bizcardproject")
            mycursor=connection.cursor()

            insert_query1=""" insert into bizcard_info values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            mycursor.executemany(insert_query1,rows)
            connection.commit()
    except:
        pass

    return df

# fetch data by its cardholder name

def fetch_data_by_name(connection,name):
     
    connection=mysql.connector.connect(host="localhost",user="root",password="12345",database="bizcardproject")
    mycursor=connection.cursor()
    query1="select Cardholder_name,Designation,Phone_number,Website_url,Email_Id,Street_number,City,State,Pincode,Company_name from bizcard_info where Cardholder_name=%s"
    value=(Cardholder_name, )
    mycursor.execute(query1,value)
    q1=mycursor.fetchall()
    df1=pd.DataFrame(q1,columns=["Cardholder_name","Designation","Phone_number","Website_url" ,"Email_Id" ,"Street_number","City","State" ,"Pincode","Company_name" ])
    return q1

#modify the data

def modify_table(connection):
      mycursor=connection.cursor()
      alter_table_query="""(ALTER TABLE bizcard_info
                        ADD COLUMN Cardholder_name varchar(100),ADD COLUMN Designation varchar(50),ADD COLUMN Phone_number varchar(50),
                        ADD COLUMN Website_url varchar(50),ADD COLUMN Email_Id varchar(50),ADD COLUMN Street_number	varchar(50),
                        ADD COLUMN City varchar(50),ADD COLUMN State varchar(50),ADD COLUMN Pincode	int,ADD COLUMN Company_name varchar(50))"""
      mycursor.execute (alter_table_query)
      connection.commit
      st.write("Table modified successfully")
        

#streamlit code


    

st.set_page_config(layout= "wide")
st.title(":green[BUSINESS CARD DATA EXTRACTION WITH OCR]")


tab1,tab2=st.tabs(["DATA_EXTRACTION","DATA_MODIFICATION"])

with tab1:

    try:

        file=st.file_uploader("select a business card (image file)",type=['png','jpg','jpeg'],accept_multiple_files=False)
        st.markdown('''File extention support: png,jpg,jpeg''')


        st.image(file,caption="image is uploaded")

    except:
        st.info("Error: Failed to process image")

    
    
    if  st.button("UPLOADING TEXT IN THE IMAGE IN DATAFRAME"):
        image=Image.open(file)
        file=np.array(image)
        insert=card_reader(file)
        st.table(insert)
        st.button("pause")


    elif st.button("VIEWING DATA FROM MYSQL"):
        
        connection=mysql.connector.connect(host="localhost",user="root",password="12345",database="bizcardproject")
        mycursor=connection.cursor()
        query1='''select *  from Bizcard_info'''
        mycursor.execute(query1)
        q1=mycursor.fetchall()
        df1=pd.DataFrame(q1,columns=["Cardholder_name","Designation","Phone_number","Website_url" ,"Email_Id" ,"Street_number",
                                "City","State" ,"Pincode","Company_name" ])
        st.write(df1)
        st.button("pause")

with tab2:

    connection=mysql.connector.connect(host="localhost",user="root",password="12345",database="bizcardproject")
    mycursor=connection.cursor()

    st.title(":blue[READ, UPDATE AND DELETE OPERATIONS IN MYSQL]")

    option=st.selectbox("select an operation",("Read","Update","Delete"))

    


    if option=="Read":

        st.subheader("Read Records")
        
        mycursor.execute("select * from bizcard_info")
        result=mycursor.fetchall()
        for row in result:
            st.write(row)

    elif option=="Update":
       
        connection=mysql.connector.connect(host="localhost",user="root",password="12345",database="bizcardproject")
        mycursor=connection.cursor()

        
        st.subheader("Update Records")
       
        
        Cardholder_name=st.selectbox("choose the name",("SANTHOSH","Amit","REVANTH","KARTHICK","Selva"))

        #if Cardholder_name=="Amit":

        result1=fetch_data_by_name(connection,Cardholder_name)

        list=[]
        for res in result1[0]:
            list.append(res)
    
        if st.button("Select"):
        

            Designation=st.text_input("Enter Designation:",value=list[1])
            Phone_number=st.text_input("Enter Phonenumber",value=list[2])
            Website_url=st.text_input("Enter Website url",value=list[3])
            Email_Id=st.text_input("Enter email id",value=list[4])
            Street_number=st.text_input("Enter Street Name",value=list[5])
            City=st.text_input("Enter city",value=list[6])
            State=st.text_input("Enter Statename",value=list[7])
            Pincode=st.number_input("Enter pincode",value=list[8])
            Company_name=st.text_input("Enter Company Name",value=list[9])

        
            
            
            if st.button("UPDATE"):
                query1="update bizcard_info set Designation=%s,Phone_number=%s,Website_url=%s,Email_Id=%s,Street_number=%s,City=%s,State=%s ,Pincode=%s,Company_name=%s where  Cardholder_name=%s"
                value=(Designation,Phone_number,Website_url,Email_Id,Street_number,City,State,Pincode,Company_name,Cardholder_name)
                mycursor.execute(query1,value)
                connection.commit()
                
                st.success("Records are successfully updated")

    elif option=="Delete":
        st.header("Deleter the record")
        Cardholder_name=st.selectbox("choose the name",("Amit","REVANTH","KARTHICK","Selva","SANTHOSH"))
        if st.button("Delete"):
            query="delete from bizcard_info where Cardholder_name=%s"
            value=(Cardholder_name,)
            mycursor.execute(query,value)
            connection.commit()
            st.success("Record Delete completely")
    

        
       



with st.sidebar:
    st.title(":blue[EXTRACTING BUSINESS CARD DATA WITH OCR ]")
    st.header(":red[STEPS FOLLOWED]")
    st.caption("Uploaded the image of the business card")
    st.caption("Extracted the relevant information from the card using easyocr")
    st.caption("Extracted information displayed in the GUI using streamlit and pandas")
    st.caption("Extracted information stored into mysql database ")
    st.caption("Displayed the mysql table in the streamlit dashboard")
    st.caption("Read,update and delete options created in the streamlit for data modification")
    st.header(":red[TECHNOLOGIES USED]")
    st.caption("EASY OCR,STREAMLIT GUI,MYSQL,PANDAS,PILLOW")

