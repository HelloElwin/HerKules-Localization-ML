import os
files = os.listdir('./cropped')
cnt = 1
for fi in files:
    os.system('mv ./cropped/' + fi + ' ./' + str(cnt) + '.jpg')
    cnt += 1
cntt = 1
files = os.listdir('./')
while cntt<cnt:
    for fii in files:
        if fii==str(cntt)+'.jpg':
            os.system('mv ' + fii + ' ./cropped/' + str(cntt) + '.jpg')
            cntt += 1
