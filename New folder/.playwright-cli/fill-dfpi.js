const { chromium } = require("playwright");
(async()=>{
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222').catch(()=>null);
  if (!browser) throw new Error('CDP not available');
  const pages = browser.contexts()[0].pages();
  const page = pages[pages.length-1];
  const text = `This complaint concerns a used 2017 Honda Civic sold and financed through Karplus Auto Sales / Karplus Warehouse, with servicing or collection later involving On Time Financing and Green Road Finance. At the time of sale in July 2020, the contract terms were not meaningfully explained before signing. Optional products were allegedly presented as required, including a tracking device, window etching, and extended warranty. There were also oral statements that no prepayment penalty would apply.

The records show payment and disclosure problems. On July 6, 2020, $4,600 was paid, followed by $1,000 on July 11, 2020, and $550.36 in August 2020. Later records state the contract reflected a $6,000 down payment while receipts reflected $5,600. The contract also included disputed charges for a Theft Deterrent Device ($695) and Surface Protection Product ($1,495), which were not clearly authorized.

There were also problems involving loan transfers, insurance, and repossession. Responsibility for GAP coverage and insurance charges was shifted between On Time, Green Road, and Karplus. The credit reporting and lender sequence appear inconsistent. In April 2023, the vehicle was repossessed in the early morning, fees and release requirements changed repeatedly, and the vehicle was allegedly damaged during repossession. The repossession company was difficult to reach, and there are concerns about notice, fee practices, and use of a duplicate key that had not been disclosed.

I request DFPI review of the sale disclosures, add-on products, payment application, insurance and GAP handling, lender-transfer practices, debt collection conduct, and repossession-related fees and damage.`;
  await page.getByRole('textbox', { name: /What happened\?/ }).fill(text);
  await browser.close();
})();
