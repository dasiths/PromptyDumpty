#!/bin/bash

echo ----------------------------------------------
echo If you want help using the prompt library or list
echo of available prompts, simply type:
echo 'What prompts are available to use?'
echo ----------------------------------------------

export NVM_DIR="/usr/local/share/nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# make NVM available and install node -lts
nvm install --lts
nvm use --lts
