# update_utility
A program designed to update the local files for the "warrant builder" program. Intended for non-technical users to update the software.

The program is intended to be run as an executable from the same directory as the warrant builder executable. If the warrant builder executable (or supporting files) are not present in the directory, this program will reach out to a known location and grab the files, as long as the calculated sha256 hash matches the posted hash. The program eliminates the problem of distributing updated software to non-technical users who aren't going to be running the warrant builder from the python source. 

Once the program has been launched, the user can elect to update the warrant builder program, at which point the updater will compare the hash of the local files against the remote files and update any that differ (again - checking for a match with the posted hash as well).

Future plans include a function to chek and update the updater itself, should that become necessary.
