JIRA OAuth1 Setup and Usage
====================

Follow these instruction while in the `token_generator/` directory of this repo.

### Python 3 Setup
* Create Python 3 Virtual Environment
```
mkvirtualenv -p python3 jira_oauth1_py3_env
```
* Activate this environment to work on
```
workon jira_oauth1_py3_env
```
* Install all required libraries
```
pip install -r requirements.txt
```

### RSA Private and Public Keys
You will need to contact cloud-ops and request the public/private keys for this applications link set uop for oAuth access to the Jira server instance. The application link is called OauthKey (I believe). Once you have them, you can begin the oAuth dance!!

* Make sure you have **.oauthconfig** folder in your home directory
* Store the RSA Private key in file **oauth.pem**
* Store the RSA Public Key in file **oauth.pub**
* Again make sure both files are *copied* to **.oauthconfig** folder in your home directory.

### Prepare for OAuth Dance 
* Configure **starter_oauth.config** with correct values
```sh
[oauth_config]
jira_base_url=https://jira.flit.tech
consumer_key=OauthKey
test_jira_issue=INT-219
```
 
Perform Jira OAuth Dance
================
* Make sure you are in the `token_generator` directory of this Repo
* Python Virtual Environment that we create earlier is active.
* Run **jira_oauth_token_generator.py**
```
(jira_oauth1_py3_env) ➜ python jira_oauth_token_generator.py
```
* If you get TypeError, **string argument without an encoding** as below, you need to update **hashAndSign** function in rsakey.py where package is installed as shown in path below.
```
(jira_oauth1_py3_env) ➜ python jira_oauth_token_generator.py
...
/../jira_oauth1_py3_env/lib/python3.6/site-packages/tlslite/utils/rsakey.py", line 62, in hashAndSign
    hashBytes = SHA1(bytearray(bytes))
TypeError: string argument without an encoding
```
  * To fix this error, add explicitly "utf8" encoding in rsakey.py in hashAndSign function
```
In function hashAndSign(...),
    *changed line* ->   hashBytes = SHA1(bytearray(bytes))
    to ->               hashBytes = SHA1(bytearray(bytes, "utf8"))
```
* Authenticate in browser as directed below and then click **y** for question *Have you authorized me?*
```
(jira_oauth1_py3_env) ➜ python jira_oauth_token_generator.py

Token:
    - oauth_token        = sdfsdf2342edfsdfwfwfwer23432423    
    - oauth_token_secret = sdfsdf2345t66w54564336sdgwtwte

Go to the following link in your browser:
https://jira.example.com/plugins/servlet/oauth/authorize?oauth_token=O2hfcGETBfKpxpvB5L6WzQc4dwaxGCPe
Have you authorized me? (y/n)
```
* After successful oAuth generation, you will get another set of values for **oauth_token** and **oauth_token_secret**. These are you tokens that you need to use access Jira without passing credentials.
> Access Token:
>    - oauth_token        = sdfPxIsdfsdfs$sdf234sdgssd$sresdf
>    - oauth_token_secret = rswfsdfsdfjsdjlksjdfljsdlkfjsldfj
>
> You may now access protected resources using the access tokens above.
>
>
> Accessing INT-219 using generated OAuth tokens:
>
> Success!
>
> Issue key: INT-219, Summary: This is INT-219 Summary

## Copy both oauth_token and oauth_token_secret to .oauth_jira_config file.
```
(jira_oauth1_py3_env) ➜  cat ~/.oauthconfig/.oauth_jira_config
[oauth_token_config]
oauth_token=sdfPxIsdfsdfs$sdf234sdgssd$sresdf
oauth_token_secret=rswfsdfsdfjsdjlksjdfljsdlkfjsldfj
consumer_key=OauthKey
user_private_key_file_name=oauth.pem

[server_info]
jira_base_url=https://jira.flit.tech
```

>Original implementation is available here: 
>
> https://bitbucket.org/atlassian_tutorial/atlassian-oauth-examples under python/app.py
