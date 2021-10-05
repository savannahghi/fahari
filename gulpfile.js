// Gulp and package
const { src, dest, parallel, series, watch } = require("gulp");
const pjson = require("./package.json");

// Plugins
const autoprefixer = require("autoprefixer");
const browserSync = require("browser-sync").create();
const cleanCSS = require("gulp-clean-css");
const del = require("del");
const gulp = require("gulp");
const merge = require("merge-stream");
const plumber = require("gulp-plumber");
const rename = require("gulp-rename");
const gulpSass = require("gulp-sass");
const dartSass = require("sass")
const sass = gulpSass(dartSass);
const uglify = require("gulp-uglify");
const concat = require("gulp-concat");
const cssnano = require("cssnano");
const imagemin = require("gulp-imagemin");
const pixrem = require("pixrem");
const postcss = require("gulp-postcss");
const reload = browserSync.reload;
const spawn = require("child_process").spawn;
const lec = require("gulp-line-ending-corrector");
const sourcemaps = require("gulp-sourcemaps");

// Relative paths function
function pathsConfig(appName) {
    this.app = `./${pjson.name}`;
    const vendorsRoot = "node_modules";

    return {
        bootstrapSass: `${vendorsRoot}/bootstrap/scss`,
        vendorsJs: [
            `${vendorsRoot}/jquery/dist/jquery.js`,
            `${vendorsRoot}/popper.js/dist/umd/popper.js`,
            `${vendorsRoot}/bootstrap/dist/js/bootstrap.js`,
            `${vendorsRoot}/bootstrap-select/dist/js/bootstrap-select.js`,
            `${vendorsRoot}/chart.js/dist/*.js`,
            `${vendorsRoot}/jszip/dist/jszip.min.js`,
            `${vendorsRoot}/pdfmake/dist/*.min.js`,
            `${vendorsRoot}/datatables.net/js/*.js`,
            `${vendorsRoot}/datatables.net-bs4/js/*.js`,
            `${vendorsRoot}/datatables.net-responsive/js/*.js`,
            `${vendorsRoot}/datatables.net-responsive-bs4/js/*.js`,
            `${vendorsRoot}/datatables.net-autofill/js/*.js`,
            `${vendorsRoot}/datatables.net-autofill-bs4/js/*.js`,
            `${vendorsRoot}/datatables.net-buttons/js/dataTables.buttons.js`,
            `${vendorsRoot}/datatables.net-buttons/js/dataTables.buttons.min.js`,
            `${vendorsRoot}/datatables.net-buttons/js/*.js`,
            `${vendorsRoot}/datatables.net-buttons-bs4/js/*.js`,
            `${vendorsRoot}/datatables.net-colreorder-bs4/js/*.js`,
            `${vendorsRoot}/datatables.net-datetime/js/*.js`,
            `${vendorsRoot}/datatables.net-fixedcolumns/js/*.js`,
            `${vendorsRoot}/datatables.net-fixedcolumns-bs4/js/*.js`,
            `${vendorsRoot}/datatables.net-fixedheader/js/*.js`,
            `${vendorsRoot}/datatables.net-fixedheader-bs4/js/*.js`,
            `${vendorsRoot}/datatables.net-keytable/js/*.js`,
            `${vendorsRoot}/datatables.net-keytable-bs4/js/*.js`,
            `${vendorsRoot}/datatables.net-rowgroup/js/*.js`,
            `${vendorsRoot}/datatables.net-rowgroup-bs4/js/*.js`,
            `${vendorsRoot}/datatables.net-rowreorder/js/*.js`,
            `${vendorsRoot}/datatables.net-rowreorder-bs4/js/*.js`,
            `${vendorsRoot}/datatables.net-scroller/js/*.js`,
            `${vendorsRoot}/datatables.net-scroller-bs4/js/*.js`,
            `${vendorsRoot}/datatables.net-searchbuilder/js/*.js`,
            `${vendorsRoot}/datatables.net-searchbuilder-bs4/js/*.js`,
            `${vendorsRoot}/datatables.net-searchpanes/js/*.js`,
            `${vendorsRoot}/datatables.net-searchpanes-bs4/js/*.js`,
            `${vendorsRoot}/datatables.net-select/js/*.js`,
            `${vendorsRoot}/datatables.net-select-bs4/js/*.js`,
            `${vendorsRoot}/jquery.easing/*.js`,
        ],
        app: this.app,
        templates: `${this.app}/templates`,
        css: `${this.app}/static/css`,
        dataTablesCSS: `${vendorsRoot}/datatables.net-bs4/css/*.css`,
        sass: `${this.app}/static/sass`,
        fonts: `${this.app}/static/fonts`,
        images: `${this.app}/static/images`,
        js: `${this.app}/static/js`,
        //        js: [
        //            `${this.app}/static/js/project.js`,
        //            `${paths.js}/user_facility_allotment_form.js`,
        //        ],
    };
}

var paths = pathsConfig();

// Styles autoprefixing and minification
function styles() {
    var processCss = [
        autoprefixer(), // adds vendor prefixes
        pixrem(), // add fallbacks for rem units
    ];

    var minifyCss = [
        cssnano({ preset: "default" }), // minify result
    ];

    return src(`${paths.sass}/project.scss`)
        .pipe(
            sass({
                includePaths: [paths.bootstrapSass, paths.sass, paths.dataTablesCSS],
            }).on("error", sass.logError)
        )
        .pipe(plumber()) // Checks for errors
        .pipe(postcss(processCss))
        .pipe(dest(paths.css))
        .pipe(rename({ suffix: ".min" }))
        .pipe(postcss(minifyCss)) // Minifies the result
        .pipe(dest(paths.css));
}

// Javascript minification
function scripts() {
    return src([
        `${paths.js}/project.js`,
        `${paths.js}/common/forms/user_facility_allotment_form.js`,
    ])
        .pipe(sourcemaps.init())
        .pipe(plumber()) // Checks for errors
        .pipe(uglify()) // Minifies the js
        .pipe(lec({ verbose: true, eolc: "LF", encoding: "utf8" }))
        .pipe(rename({ suffix: ".min" }))
        .pipe(sourcemaps.write())
        .pipe(dest(paths.js));
}
// Vendor Javascript minification
function vendorScripts() {
    return src(paths.vendorsJs)
        .pipe(sourcemaps.init())
        .pipe(concat("vendors.js"))
        .pipe(lec({ verbose: true, eolc: "LF", encoding: "utf8" }))
        .pipe(dest(paths.js))
        .pipe(plumber()) // Checks for errors
        .pipe(uglify()) // Minifies the js
        .pipe(rename({ suffix: ".min" }))
        .pipe(sourcemaps.write())
        .pipe(dest(paths.js));
}

// Image compression
function imgCompression() {
    return src(`${paths.images}/*`)
        .pipe(imagemin()) // Compresses PNG, JPEG, GIF and SVG images
        .pipe(dest(paths.images));
} // Run django server
function asyncRunServer() {
    var cmd = spawn(
        "gunicorn", ["config.asgi", "-k", "uvicorn.workers.UvicornWorker", "--reload"], { stdio: "inherit" }
    );
    cmd.on("close", function (code) {
        console.log("gunicorn exited with code " + code);
    });
}

// Browser sync server for live reload
function initBrowserSync() {
    browserSync.init(
        [`${paths.css}/**/*.css`, `${paths.js}/**/*.js`, `${paths.templates}/**/*.html`], {
        // https://www.browsersync.io/docs/options/#option-proxy
        proxy: {
            target: "django:8000",
            proxyReq: [
                function (proxyReq, req) {
                    // Assign proxy "host" header same as current request at Browsersync server
                    proxyReq.setHeader("Host", req.headers.host);
                },
            ],
        },
        // https://www.browsersync.io/docs/options/#option-open
        // Disable as it doesn't work from inside a container
        open: false,
    }
    );
}

// Watch
function watchPaths() {
    console.dir(paths, { depth: null });
    watch(`${paths.sass}/*.scss`, { usePolling: true }, styles);
    watch(`${paths.templates}/**/*.html`, { usePolling: true }).on(
        "change",
        reload
    );
    watch(
        [`${paths.js}/**/*.js`, `!${paths.js}/**/*.min.js`], { usePolling: true },
        scripts
    ).on("change", reload);
}

// Generate all assets
const generateAssets = parallel(styles, scripts, vendorScripts, imgCompression);

// Set up dev environment
const dev = parallel(initBrowserSync, watchPaths);
exports.default = series(generateAssets, dev);
exports["generate-assets"] = generateAssets;
exports["dev"] = dev;
