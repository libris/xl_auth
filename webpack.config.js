const path = require('path');
const webpack = require('webpack');

/*
 * Webpack Plugins
 */
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

// take debug mode from the environment
const debug = (process.env.NODE_ENV !== 'production');

const rootAssetPath = path.join(__dirname, 'assets');

module.exports = {
    // configuration
    context: __dirname,
    entry: {
        main_js: './assets/js/main',
        main_css: [
            path.join(__dirname, 'node_modules', '@fortawesome', 'fontawesome-free', 'css', 'all.css'),
            path.join(__dirname, 'assets', 'css', 'style.less')
        ]
    },
    mode: debug,
    output: {
        path: __dirname + '/xl_auth/static/build',
        publicPath: '/static/build/',
        filename: '[name].bundle.js',
        chunkFilename: '[id].js'
    },
    resolve: {
        extensions: ['.js', '.jsx', '.css', '.less']
    },
    devtool: debug ? 'eval-source-map' : false,
    module: {
        rules: [
            {
                test: /\.less$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                        options: {}
                    },
                    'css-loader',
                    'less-loader'
                ]
            },
            {
                test: /\.css$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                        options: {}
                    },
                    'css-loader'
                ]
            },
            {test: /\.html$/, loader: 'raw-loader'},
            {
                test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
                loader: 'url-loader',
                options: {limit: 10000, mimetype: 'application/font-woff'}
            },
            {
                test: /\.(ttf|eot|svg|png|jpe?g|gif|ico)(\?.*)?$/i,
                loader: 'file-loader',
                options: {context: rootAssetPath, name: '[path][name].[ext]'}
            },
            {
                test: /\.js$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
                options: {presets: ['@babel/preset-env'], cacheDirectory: true}
            }
        ]
    },
    plugins: [
        new MiniCssExtractPlugin({filename: '[name].bundle.css'}),
        new webpack.ProvidePlugin({$: 'jquery', jQuery: 'jquery'})
    ].concat(debug ? [] : [
        // production webpack plugins go here
        new webpack.DefinePlugin({
            'process.env': {
                'NODE_ENV': JSON.stringify('production')
            }
        })
    ])
};
