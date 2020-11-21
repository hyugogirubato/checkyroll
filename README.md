# checkyroll
Crunchyroll and funimation account checker. Allows you to retrieve all the information for an account using the username and password only.

## Prerequisite
 - Python 3.7
 
 ## Command line
main -i <input> -t <type> -c <config>
main --input <input> -type <type> -config <config>
  
## Info
 - The <input> value can be a list of accounts in a .txt file in the form "username: password" or directly "username: password".
 - The type is either "crunchyroll" or "funimation".
 - The "--config" or "-c" argument is optional. This is the application of custom settings when saving / viewing results. You will find an example of the config.json file. Default values are True
 - It is recommended to use a VPN when testing.
 - If too many invalid funimation IDs are tested next. The checker will not work for funimation for a while.
 - If the crunchyroll API blocks the connection. Just use a VPN.
 
 -----------------
 *This software was created by [__Nashi Team__](https://discord.com/invite/g6JzYbh).  
Find us on [discord](https://discord.com/invite/g6JzYbh) for more information on projects in development.*
 
 
