/**
 * Download India GeoJSON and save locally
 * Run this once: node download-india-map.js
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const url = 'https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson';
const outputPath = path.join(__dirname, 'features', 'india-map-data.json');

console.log('Downloading India GeoJSON...');

https.get(url, (response) => {
    let data = '';
    
    response.on('data', (chunk) => {
        data += chunk;
    });
    
    response.on('end', () => {
        try {
            // Validate JSON
            const geoJSON = JSON.parse(data);
            
            // Save to file
            fs.writeFileSync(outputPath, JSON.stringify(geoJSON, null, 2));
            
            console.log('✓ India GeoJSON downloaded successfully!');
            console.log(`✓ Saved to: ${outputPath}`);
            console.log(`✓ Features: ${geoJSON.features.length} states/UTs`);
        } catch (error) {
            console.error('✗ Failed to parse GeoJSON:', error.message);
        }
    });
}).on('error', (error) => {
    console.error('✗ Download failed:', error.message);
    console.log('\nAlternative: Download manually from:');
    console.log('https://github.com/geohacker/india/blob/master/state/india_state.geojson');
    console.log('Save as: features/india-map-data.json');
});
