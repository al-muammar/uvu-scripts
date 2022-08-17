# Install pyenv
curl https://pyenv.run | bash

# Add the lines between EOM marker to ~/.bashrc file
cat >> ~/.bashrc <<-'EOM'

# pyenv
export PATH="/home/$USER/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
EOM

export PATH="/home/$USER/.pyenv/bin:$PATH"
# Install python
pyenv install 3.7.6
pyenv global 3.7.6
# Install pyenv virtualenvwrapper
git clone https://github.com/pyenv/pyenv-virtualenvwrapper.git $(pyenv root)/plugins/pyenv-virtualenvwrapper
echo "pyenv virtualenvwrapper" >> ~/.bashrc

# Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Reload shell to apply changes
exec $SHELL

