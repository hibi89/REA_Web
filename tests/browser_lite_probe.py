from pathlib import Path
import asyncio,hashlib,tempfile
from playwright.async_api import async_playwright
from rea.lite_builder import build_lite

async def main():
 with tempfile.TemporaryDirectory(prefix='rea-lite-browser-') as temp:
  root=Path(temp);csv=root/'data.csv';csv.write_text('source_id,display,group,notes\nA01,콜드브루,카페,첫 메뉴\nA02,라떼,카페,둘째 메뉴\nA03,재고표,사무,셋째 메뉴\n',encoding='utf8')
  out=root/'out.html';build_lite(csv,out,mapping=dict(id='source_id',title='display',category='group'),expected_sha256=hashlib.sha256(csv.read_bytes()).hexdigest(),confirmation='APPROVE',theme='cafe',name='REA 데모')
  async with async_playwright() as ap:
   browser=await ap.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
   ctx=await browser.new_context(accept_downloads=True)
   page=await ctx.new_page();errors=[];network=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:network.append(r.url))
   await page.set_content(out.read_text(encoding='utf8'),wait_until='domcontentloaded')
   print('initial status',await page.locator('#pagination').inner_text(),'rows',await page.locator('#items tr').count(),'body', (await page.locator('body').inner_text())[:200])
   assert await page.locator('#items tr').count()==3
   await page.locator('#search').fill('라떼');assert await page.locator('#items tr').count()==1
   await page.locator('#search').fill('');await page.locator('#category').select_option('사무');assert await page.locator('#items tr').count()==1
   await page.locator('#category').select_option('');await page.locator('#items tr button').first.click();assert 'source_id' not in await page.locator('#detail').inner_text();assert 'id : A02' in await page.locator('#detail').inner_text()
   await page.locator('#csv-file').set_input_files({'name':'invalid.csv','mimeType':'text/csv','buffer':'id,title,category\nA01,A,B\n'.encode()})
   assert '이전 데이터는 유지' in await page.locator('#message').inner_text();assert await page.locator('#items tr').count()==3
   good='id,title,category,notes\nX01,"새 이름",소모품,"따옴표 ""인용"""\nX02,두번째,소모품,좋음\n'
   await page.locator('#csv-file').set_input_files({'name':'good.csv','mimeType':'text/csv','buffer':good.encode()})
   print('import msg',await page.locator('#message').inner_text())
   assert await page.locator('#items tr').count()==2
   assert await page.locator('#items tr').first.locator('td').first.inner_text()=='두번째' # title sort
   # Reimport using original, owner-approved noncanonical source headers.
   original_update='source_id,display,group,notes\nY01,원본열 업데이트,사무,메모\nY02,원본열 또 하나,사무,메모\n'
   await page.locator('#csv-file').set_input_files({'name':'original.csv','mimeType':'text/csv','buffer':original_update.encode()})
   assert await page.locator('#items tr').count()==2
   assert '원본열 업데이트' in await page.locator('#items').inner_text()

   async with page.expect_download() as dl:
    await page.locator('#export').click()
   d=await dl.value;path=await d.path();new=Path(path).read_text(encoding='utf8');print('download',d.suggested_filename,'len',len(new))
   assert 'Y01' in new and '원본열 업데이트' in new
   page2=await ctx.new_page();page2.on('pageerror',lambda e:errors.append(str(e)));page2.on('request',lambda r:network.append(r.url))
   await page2.set_content(new,wait_until='domcontentloaded')
   assert await page2.locator('#items tr').count()==2
   assert '원본열' in await page2.locator('#items tr').first.locator('td').first.inner_text()
   malicious='id,title,category,notes\nX03,"</script><img src=x onerror=alert(1)>",시연,안전한 텍스트\n'
   await page2.locator('#csv-file').set_input_files({'name':'attack.csv','mimeType':'text/csv','buffer':malicious.encode()})
   assert await page2.locator('#items tr').count()==1
   assert await page2.locator('img').count()==0
   async with page2.expect_download() as dl2:
    await page2.locator('#export').click()
   injection_html=Path(await (await dl2.value).path()).read_text(encoding='utf8')
   assert '</script><img' not in injection_html
   page3=await ctx.new_page();page3.on('pageerror',lambda e:errors.append(str(e)));page3.on('request',lambda r:network.append(r.url))
   await page3.set_content(injection_html,wait_until='domcontentloaded')
   assert await page3.locator('#items tr').count()==1 and await page3.locator('img').count()==0
   assert 'alert(1)' in await page3.locator('#items tr').first.inner_text()
   bulk='id,title,category,notes\n'+''.join(f'R{j:03d},상품{j:03d},카테고리,정보\n' for j in range(145))
   await page3.locator('#csv-file').set_input_files({'name':'many.csv','mimeType':'text/csv','buffer':bulk.encode()})
   assert await page3.locator('#items tr').count()==60
   await page3.locator('#next').click();assert await page3.locator('#items tr').count()==60
   await page3.locator('#next').click();assert await page3.locator('#items tr').count()==25
   assert '3 / 3' in await page3.locator('#pagination').inner_text()
   await page3.locator('#prev').click();assert await page3.locator('#items tr').count()==60
   await page3.locator('#csv-file').set_input_files({'name':'bad.csv','mimeType':'text/csv','buffer':b'id,title,category,notes\nR001,"unclosed,x,z'})
   assert await page3.locator('#items tr').count()==60 and '이전 데이터는 유지' in await page3.locator('#message').inner_text()
   print('pagination 145 60/60/25, injection safe, malformed retain; errors',errors,'network',network)
   print('reopen rows',await page2.locator('#items tr').count(),'errors',errors,'network',network)
   assert not errors and not network
   await browser.close()

if __name__=='__main__':asyncio.run(main())
