const esbuild = require('esbuild');

// Function to generate AST using Esbuild
async function generateAST(jsCode) {
    try {
        const result = await esbuild.analyzeModules({
            stdin: {
                contents: jsCode,
                resolveDir: '.', // Specify the directory for resolution
            },
        });

        // Output the AST
        console.log(JSON.stringify(result, null, 2));
    } catch (error) {
        console.error("Error generating AST:", error);
        process.exit(1); // Exit with an error code
    }
}

// Get JavaScript code from command line arguments
const jsCode = process.argv.slice(2).join('\n');

// Generate the AST
generateAST(jsCode);
