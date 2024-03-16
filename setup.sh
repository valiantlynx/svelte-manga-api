docker build -t python-development-environment-image .
docker run --name python-development-environment-container -d -p 8000:8000 -v $(pwd):/code python-development-environment-image

#connect to turborepo
git subtree add --prefix=apps/python-development-environment https://github.com/valiantlynx/python-development-environment.git main --squash
git subtree pull --prefix=apps/python-development-environment https://github.com/valiantlynx/python-development-environment.git main --squash
git subtree push --prefix=apps/python-development-environment https://github.com/valiantlynx/python-development-environment.git main