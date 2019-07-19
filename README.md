# Course-Timing-Calc

This tool estimates how long a course will take to teach to students. It automatically reads the course structure (modules/lessons/topics) from Xyleme and presents it to the user. The user can specify what time the day starts and ends, as well as a lunch time and its duration. Then for each lesson/topic, an estimated teach time can be specified. The tool automatically recalculates as the estimations change. It will push lessons/topics to the next/previous day if needed, depending on the teach times and the start and end times. 

## Instructions
  
- To run mongod server:
  
    - Go to bin directory:
    
    ```
    
      cd Downloads\mongodb-win32-x86_64-2008plus-ssl-4.0.10\mongodb-win32-x86_64-2008plus-ssl-4.0.10\bin
      
    ```
    
    - Run mongod server:
    
    ```
    
      mongod

    ```
  
- In Pycharm terminal:
  
  - Install necessary packages:

    ```
      
      pip install -r requirements.txt

    ```
  
  - Specify how to load the application: 
    
    ```  
    
      set FLASK_APP=main.py
      
    ```
   
  - Set Xyleme credentials:
    
    ```
    
      set XYLEME_USERNAME=______
      set XYLEME_PASSWORD=______
  
    ```
    
  - To run the application:
      - For Production mode:

        ```

        set XYLEME_API=https://vmware.xyleme.com
        set XYLEME_MEDIA=https://sps-eu.xyleme.com/vmware
      
        ```
      
      - For Testing mode:

        ```

        set XYLEME_API=http://127.0.0.1:9999
        set XYLEME_MEDIA=http://127.0.0.1:9999

        ```
        
      ```
        
      flask run
        
      ```
        
