
del qbit/resources.py

cd resources

python build_resources.py > images.qrc

pyrcc5 -o resources.py images.qrc
move /Y resources.py ../qbit/resources.py

del images.qrc

cd ..
