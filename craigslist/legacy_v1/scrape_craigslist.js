const puppeteer = require('puppeteer');
const fs = require('fs');
const axios = require('axios');
require('dotenv').config();

const city = process.argv[2] || 'charlotte';
const baseUrl = `https://${city}.craigslist.org`;

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function randomDelay(min = 1000, max = 3000) {
    return delay(Math.floor(Math.random() * (max - min + 1)) + min);
}

function getRandomUserAgent() {
    const userAgents = [/* your user agents here */];
    return userAgents[Math.floor(Math.random() * userAgents.length)];
}

async function extractContactInfo(text) {
    const HF_TOKEN = process.env.HF_TOKEN;
    console.log("Loaded token prefix:", HF_TOKEN?.slice(0, 10));

    const apiUrl = 'https://router.huggingface.co/hf-inference/models/dslim/bert-base-NER';

    try {
        const response = await axios.post(apiUrl, {
            inputs: text.slice(0, 400)
        }, {
            headers: {
                Authorization: `Bearer ${HF_TOKEN}`
            },
            timeout: 10000
        });

        const entities = response.data?.[0] || [];

        let email = 'NO EMAIL';
        let phone = 'NO PHONE';
        let website = 'NO WEBSITE';

        const emailMatch = text.match(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,}\b/i);
        const phoneMatch = text.match(/(\+?\d{1,3})?[\s\-.(]*\d{3}[\s\-.)]*\d{3}[\s\-]*\d{4}/);
        const urlMatch = text.match(/\bhttps?:\/\/[^\s<>"']+/i);

        if (emailMatch) email = emailMatch[0];
        if (phoneMatch) phone = phoneMatch[0];
        if (urlMatch) website = urlMatch[0];

        return { email, phone, website };

    } catch (err) {
        console.error('Error with Hugging Face API:', err.message);
        return { email: 'ERROR', phone: 'ERROR', website: 'ERROR' };
    }
}

async function createBrowser() {
    const userAgent = getRandomUserAgent();
    const launchOptions = {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu',
            `--user-agent=${userAgent}`
        ]
    };
    const browser = await puppeteer.launch(launchOptions);
    return { browser, userAgent };
}

async function navigateWithRetry(page, url, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            await page.goto(url, {
                waitUntil: 'networkidle2',
                timeout: 30000
            });
            return true;
        } catch (error) {
            console.log(`Navigation attempt ${attempt} failed for ${url}: ${error.message}`);
            if (attempt === maxRetries) {
                throw error;
            }
            await randomDelay(2000, 5000);
        }
    }
}

async function scrapeCraigslist() {
    let browser;
    try {
        ({ browser } = await createBrowser());
        const page = await browser.newPage();

        await page.setExtraHTTPHeaders({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        });

        const url = `${baseUrl}/search/lss?cc=gb`;
        console.log(`Navigating to: ${url}`);

        await navigateWithRetry(page, url);
        await delay(3000 + Math.random() * 2000);

        let listings = await page.evaluate((baseUrl) => {
            return Array.from(document.querySelectorAll('a[href*="/lss/"]'))
                .map(link => {
                    const title = link.textContent?.trim() || link.getAttribute('title') || '';
                    let href = link.getAttribute('href');
                    if (!href) return null;

                    if (href.startsWith('/')) {
                        href = baseUrl + href;
                    } else if (!href.startsWith('http')) {
                        href = baseUrl + '/' + href;
                    }

                    return {
                        title: title.replace(/[\n\r\t]/g, ' ').replace(/,/g, ';'),
                        link: href
                    };
                })
                .filter(item => item && item.title && item.link);
        }, baseUrl);

        const seenTitles = new Set();
        listings = listings.filter(({ title }) => {
            const normalizedTitle = title.toLowerCase();
            if (seenTitles.has(normalizedTitle)) return false;
            seenTitles.add(normalizedTitle);
            return true;
        });

        console.log(`Found ${listings.length} unique listings`);

        const detailedListings = [];

        for (let i = 0; i < listings.length; i++) {
            const { title, link } = listings[i];
            console.log(`Scraping ${i + 1}/${listings.length}: ${title}`);

            try {
                const detailPage = await browser.newPage();

                await detailPage.setExtraHTTPHeaders({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                });

                await navigateWithRetry(detailPage, link);
                await randomDelay(1500, 3000);

                const body = await detailPage.evaluate(() => {
                    const bodyEl = document.querySelector('#postingbody');
                    if (!bodyEl) return '';
                    return bodyEl.innerText.trim().replace(/[\n\r\t]/g, ' ').replace(/,/g, ';');
                });

                await detailPage.close();

                const contactInfo = await extractContactInfo(`${title} ${body}`);
                detailedListings.push({ title, link, body, ...contactInfo });

            } catch (err) {
                console.error(`Error scraping ${link}:`, err.message);
                detailedListings.push({
                    title,
                    link,
                    body: 'Error retrieving body',
                    email: 'ERROR',
                    phone: 'ERROR',
                    website: 'ERROR'
                });
            }

            await randomDelay(2000, 4000);
        }

        const csv = ['Title,Link,Body,Email,Phone,Website', ...detailedListings.map(l =>
            `"${l.title}","${l.link}","${l.body}","${l.email}","${l.phone}","${l.website}"`
        )].join('\n');

        const filename = `craigslist_${city}_full_${new Date().toISOString().split('T')[0]}.csv`;
        fs.writeFileSync(filename, csv, 'utf8');

        console.log(`Done. Data saved to ${filename}`);
        console.log(`Total listings scraped: ${detailedListings.length}`);

    } catch (error) {
        console.error('Critical error:', error.message);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

process.on('SIGINT', async () => {
    console.log('\nReceived SIGINT. Gracefully shutting down...');
    process.exit(0);
});

scrapeCraigslist().catch(console.error);
