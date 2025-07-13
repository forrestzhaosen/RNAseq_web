module.exports = {
    apps: [{
        name: 'rnaseq-backend',
        script: '.venv/bin/gunicorn',
        args: '-c gunicorn.conf.py app:app',
        cwd: process.env.HOME + '/RNAseq_web',
        env: {
            FLASK_ENV: 'production'
        }
    }]
}
