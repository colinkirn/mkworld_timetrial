function styleActivePage()
{
    const navLinks = document.querySelectorAll("nav a");
    navLinks.forEach((link) => {
        const currentPath = window.location.pathname.slice("1");
        const hrefArray = link.href.split("/");
        const thisPath = hrefArray[hrefArray.length - 1];

        if (currentPath === thisPath) 
        {
            link.classList.add("active");
        }
    });
}